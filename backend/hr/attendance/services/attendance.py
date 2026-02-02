from __future__ import annotations
import logging
from datetime     import datetime, date, timedelta
from django.db    import transaction
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
    def finalize_daily_register(register: DailyRegister) -> None:
        """ Consolidates daily statistics and locks the registry for administrative review. """
        sheets = register.sheets.all()
        register.total_absences = sheets.filter(status=TimeSheetStatus.ABSENT).count()
        register.total_employees_expected = sheets.exclude(status=TimeSheetStatus.HOLIDAY).count()
        register.is_finalized = True
        register.save()
        
        master_key = generate_cache_key("hr:attendance:register:master", register.date)
        invalidate_cache_keys(master_key)

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

