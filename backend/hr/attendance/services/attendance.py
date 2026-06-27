from __future__ import annotations
import logging
from datetime   import datetime, date, timedelta
from django.db  import transaction
from django.utils import timezone

from hr.attendance.models import (
    TimeSheet, 
    DailyRegister, 
    TimePunch,
    ShiftDetail
)
from hr.attendance.enums  import PunchType, TimeSheetStatus
from .scheduling          import SchedulingService
from hr.calendar.services import CalendarService
# Cache integration
from .cache import AttendanceCacheService
from hr.services.cache_helpers import generate_cache_key, invalidate_cache_keys


logger = logging.getLogger(__name__)


class AttendanceService:
    """ Core processing engine for employee attendance and hours calculation. """

    @staticmethod
    @transaction.atomic
    def get_or_create_daily_register(target_date: date) -> DailyRegister:
        """ Retrieves or initializes the daily attendance registry. """
        register = AttendanceCacheService.get_daily_register(target_date)
        if not register:
            register, _ = DailyRegister.objects.get_or_create(date=target_date)
        return register

    @staticmethod
    def compute_timesheet_totals(timesheet: TimeSheet) -> TimeSheet:
        """ Calculates total work hours, breaks, overtime, and shortfall for a timesheet. """
        # 1. Theoretical Truth (Schedule & Policies)
        schedule = SchedulingService.get_expected_schedule(timesheet.employee, timesheet.register.date)
        punches = AttendanceCacheService.get_punches_for_date(timesheet.employee, timesheet.register.date)
        
        # 2. Raw Presence calculation
        total_work, total_break, has_manual_break = AttendanceService._calculate_durations(punches)

        # 3. Automatic break deduction if none recorded
        if not has_manual_break and schedule and schedule.break_duration:
            theoretical_break = schedule.break_duration
            if total_work > (theoretical_break * 2): 
                total_work -= theoretical_break
                total_break = theoretical_break

        timesheet.recorded_work = total_work
        timesheet.recorded_break = total_break

        # 4. Contextual Logic (Holiday vs Work Day)
        is_holiday = CalendarService.is_non_working_day(
            timesheet.register.date, 
            getattr(timesheet.employee, 'nationality', 'CD')
        )

        if is_holiday or not schedule:
            AttendanceService._handle_off_day_logic(timesheet, total_work, is_holiday)
        else:
            AttendanceService._handle_work_day_logic(timesheet, punches, schedule, total_work)

        timesheet.save()
        AttendanceCacheService.clear_employee_cache(timesheet.employee)
        return timesheet

    @staticmethod
    @transaction.atomic
    def finalize_daily_register(target_date: date) -> DailyRegister:
        """ Finalizes the daily register: auto-closes orphan punches,
            computes all timesheets, consolidates stats, and locks the day. """
        # 1. Get or create the register for this date
        register, _ = DailyRegister.objects.get_or_create(date=target_date)

        # 2. Auto-close any punches without end_at (employee forgot clock-out)
        AttendanceService._close_orphan_punches(target_date)

        # 3. Compute every timesheet for this day
        sheets = register.sheets.select_related('employee').all()
        for sheet in sheets:
            AttendanceService.compute_timesheet_totals(sheet)

        # Refresh to get updated statuses
        sheets = register.sheets.all()

        # 4. Consolidate statistics
        register.total_absences = sheets.filter(status=TimeSheetStatus.ABSENT).count()
        register.total_excused = sheets.filter(status=TimeSheetStatus.EXCUSED).count()
        register.total_employees_expected = sheets.exclude(status=TimeSheetStatus.HOLIDAY).count()
        register.is_finalized = True
        register.save()

        # 5. Invalidate cache
        master_key = generate_cache_key("hr:attendance:register:master", register.date)
        invalidate_cache_keys(master_key)

        logger.info(
            "Daily register finalized",
            extra={
                "date": target_date,
                "register_id": register.id,
                "total_sheets": sheets.count(),
                "total_absences": register.total_absences,
                "total_expected": register.total_employees_expected,
            },
        )

        return register

    # --- Orphan Punch Auto-Close ---

    @staticmethod
    def _close_orphan_punches(target_date: date) -> None:
        """ Closes any open WORK punch without end_at by setting
            end_at to the employee's scheduled end_time for that date.
            If no schedule is found, the punch is left open (HR will handle it). """
        open_punches = TimePunch.objects.filter(
            timesheet__register__date=target_date,
            punch_type=PunchType.WORK,
            end_at__isnull=True,
        ).select_related('timesheet__employee').only(
            'id', 'start_at', 'timesheet__employee',
            'timesheet__register__date',
        )

        closed_count = 0
        for punch in open_punches:
            employee = punch.timesheet.employee
            schedule = SchedulingService.get_expected_schedule(employee, target_date)
            if not schedule:
                continue  # No schedule → leave open for manual HR fix

            # Combine schedule.end_time with punch date
            naive_end = datetime.combine(target_date, schedule.end_time)
            end_at = timezone.make_aware(naive_end)

            punch.end_at = end_at
            punch.is_manual_entry = True  # Mark as auto-closed
            punch.save()
            closed_count += 1

        if closed_count:
            logger.info(
                "Auto-closed orphan punches",
                extra={"date": target_date, "count": closed_count},
            )

    # --- Internal Logic ---

    @staticmethod
    def _calculate_durations(punches: list[TimePunch]) -> tuple[timedelta, timedelta, bool]:
        """ Aggregates work and break durations from punch segments. """
        work_dur = timedelta()
        break_dur = timedelta()
        has_manual_break = False

        for punch in punches:
            if punch.end_at:
                duration = punch.end_at - punch.start_at
                if punch.punch_type == PunchType.WORK:
                    work_dur += duration
                elif punch.punch_type == PunchType.BREAK:
                    break_dur += duration
                    has_manual_break = True
        
        return work_dur, break_dur, has_manual_break

    @staticmethod
    def _handle_off_day_logic(timesheet: TimeSheet, total_work: timedelta, is_holiday: bool):
        """ Processes attendance for holidays or non-scheduled work days. """
        timesheet.status = TimeSheetStatus.HOLIDAY if is_holiday else \
                          (TimeSheetStatus.PRESENT if total_work > timedelta() else TimeSheetStatus.ABSENT)
        timesheet.overtime = total_work 
        timesheet.shortfall = timedelta(0)

    @staticmethod
    def _handle_work_day_logic(
        timesheet: TimeSheet, 
        punches: list[TimePunch], 
        schedule: ShiftDetail, 
        total_work: timedelta
    ):
        """ Processes attendance for standard scheduled work days. """
        settings = AttendanceCacheService.get_settings()
        work_punches = sorted([p for p in punches if p.punch_type == PunchType.WORK], key=lambda x: x.start_at)
        
        # 1. Lateness Detection
        if not work_punches:
            timesheet.status = TimeSheetStatus.ABSENT
        else:
            naive_start = datetime.combine(timesheet.register.date, schedule.start_time)
            expected_start = timezone.make_aware(naive_start)
            delay = max(work_punches[0].start_at - expected_start, timedelta(0))
            
            timesheet.status = TimeSheetStatus.LATE if delay > settings.late_grace_period else TimeSheetStatus.PRESENT

        # 2. Overtime & Shortfall Reconciliation
        s_dt = datetime.combine(date.min, schedule.start_time)
        e_dt = datetime.combine(date.min, schedule.end_time)
        if e_dt < s_dt: e_dt += timedelta(days=1) 
        
        expected_duration = e_dt - s_dt

        if total_work > expected_duration:
            timesheet.overtime = total_work - expected_duration
            timesheet.shortfall = timedelta(0)
        else:
            timesheet.shortfall = expected_duration - total_work
            timesheet.overtime = timedelta(0)

        # 3. Partial Absence Check
        if total_work > timedelta(0) and timesheet.shortfall > settings.partial_absence_threshold:
            timesheet.status = TimeSheetStatus.PARTIAL

