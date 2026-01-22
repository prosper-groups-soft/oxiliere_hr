from __future__ import annotations
from datetime import datetime, date, timedelta
from django.db import transaction
from django.utils import timezone
from hr.attendance.models import (
    TimeSheet, 
    DailyRegister, 
    PunchType, 
    TimeSheetStatus,
    AttendanceSettings
)
from .scheduling import SchedulingService
from hr.calendar.services import CalendarService


class AttendanceService:
    """
    Core service responsible for calculating daily attendance totals,
    detecting lateness, and computing overtime/shortfall.
    """

    @staticmethod
    @transaction.atomic
    def get_or_create_daily_register(target_date: date) -> DailyRegister:
        """
        Initializes or retrieves the DailyRegister for a given date.
        This acts as the master container for all employee timesheets of that day.
        """
        register, created = DailyRegister.objects.get_or_create(date=target_date)
        return register

    @staticmethod
    def compute_timesheet_totals(timesheet: TimeSheet) -> TimeSheet:
        """
        Main calculation engine. 
        1. Aggregates all TimePunches (Work vs Break).
        2. Compares real timestamps with the theoretical schedule (SchedulingService).
        3. Determines Attendance Status (Present, Late, Absent).
        4. Calculates Overtime and Shortfall durations.
        """
        # Load global settings for thresholds
        settings = AttendanceSettings.load()

        # 1. Fetch expected schedule (Now returns None if Holiday thanks to our previous change)
        schedule = SchedulingService.get_expected_schedule(timesheet.employee, timesheet.register.date)
        
        # 2. Sum up worked durations and breaks from completed punch segments
        punches = timesheet.punches.all()
        total_work = timedelta()
        total_break = timedelta()

        for punch in punches:
            if punch.end_at:  # We only calculate duration for closed segments
                if punch.punch_type == PunchType.WORK:
                    total_work += punch.duration
                elif punch.punch_type == PunchType.BREAK:
                    total_break += punch.duration

        timesheet.recorded_work = total_work
        timesheet.recorded_break = total_break

        # 3. Special Logic for Non-Working Days (No schedule)
        is_non_working_day = CalendarService.is_non_working_day(
            timesheet.register.date, 
            getattr(timesheet.employee, 'country_code', 'CD')
        )

        if is_non_working_day:
            timesheet.status = TimeSheetStatus.HOLIDAY
            # Every worked minute on a holiday is Overtime
            timesheet.overtime = total_work
            timesheet.shortfall = timedelta(0)
            
        elif not schedule:
            # Weekend or unscheduled day (not a holiday)
            timesheet.status = TimeSheetStatus.PRESENT if total_work > timedelta() else TimeSheetStatus.ABSENT
            timesheet.overtime = total_work # Any work on weekend/off-day is also overtime
            timesheet.shortfall = timedelta(0)

        else:
            # --- NORMAL WORKING DAY LOGIC ---
            # Identify the first work segment to check for lateness
            first_work_punch = punches.filter(punch_type=PunchType.WORK).order_by('start_at').first()
            
            if not first_work_punch:
                timesheet.status = TimeSheetStatus.ABSENT
            else:
                # Timezone-aware comparison: combine date and time then make aware
                naive_expected_start = datetime.combine(timesheet.register.date, schedule.start_time)
                expected_start = timezone.make_aware(naive_expected_start)
                
                actual_start = first_work_punch.start_at
                
                # Calculate delay (only if actual start is after expected)
                if actual_start > expected_start:
                    delay = actual_start - expected_start
                else:
                    delay = timedelta(0)
                
                # Apply grace period threshold from global settings
                if delay > settings.late_grace_period:
                    timesheet.status = TimeSheetStatus.LATE
                else:
                    timesheet.status = TimeSheetStatus.PRESENT

            # 4. Compute Overtime and Shortfall based on theoretical duration
            if schedule.end_time and schedule.start_time:
                # Calculate theoretical shift duration (handles night shifts crossing midnight)
                start_dt = datetime.combine(date.min, schedule.start_time)
                end_dt = datetime.combine(date.min, schedule.end_time)
                if end_dt < start_dt:
                    end_dt += timedelta(days=1)
                
                expected_duration = end_dt - start_dt
                
                # Final reconciliation of hours
                if timesheet.recorded_work > expected_duration:
                    timesheet.overtime = timesheet.recorded_work - expected_duration
                    timesheet.shortfall = timedelta(0)
                else:
                    timesheet.shortfall = expected_duration - timesheet.recorded_work
                    timesheet.overtime = timedelta(0)
                
                # Refine status for partial absences using dynamic threshold from settings
                if total_work > timedelta(0) and timesheet.shortfall > settings.partial_absence_threshold:
                    timesheet.status = TimeSheetStatus.PARTIAL

        timesheet.save()
        return timesheet

    @staticmethod
    def finalize_daily_register(register: DailyRegister) -> None:
        """
        Closes the daily register by aggregating statistics from all child timesheets.
        Calculates total absences and expected headcount for the dashboard.
        """
        sheets = register.sheets.all()
        
        # We count absences normally
        register.total_absences = sheets.filter(status=TimeSheetStatus.ABSENT).count()
        
        # Expected employees: We exclude those on holiday status to keep ratios accurate
        register.total_employees_expected = sheets.exclude(status=TimeSheetStatus.HOLIDAY).count()
        
        register.is_finalized = True
        register.save()

