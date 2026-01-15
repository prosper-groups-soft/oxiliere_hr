from __future__ import annotations
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from hr.attendance.models import (
    TimeSheet, 
    TimePunch, 
    AttendanceSettings
)
from .scheduling import SchedulingService


class ValidationService:
    """
    Service dedicated to ensuring data integrity and detecting 
    anomalies in employee punches.
    """

    @staticmethod
    def validate_punch_sequence(timesheet: TimeSheet) -> list[str]:
        """
        Analyzes the sequence of punches for a specific timesheet to find logical errors.
        Returns a list of error messages (strings).
        """
        errors = []
        punches = timesheet.punches.all().order_by('start_at')
        
        if not punches.exists():
            return [_("No punches found for this timesheet.")]

        last_punch = None
        for punch in punches:
            # 1. Check for overlapping punches
            if last_punch and last_punch.end_at and punch.start_at < last_punch.end_at:
                errors.append(
                    _("Overlap detected between {last_type} and {current_type} at {time}.").format(
                        last_type=last_punch.get_punch_type_display(),
                        current_type=punch.get_punch_type_display(),
                        time=punch.start_at.strftime("%H:%M")
                    )
                )

            # 2. Check for missing end_at (unclosed segments)
            # Only the very last punch of the sequence is allowed to have end_at=None 
            # (if the employee is currently working).
            if punch != punches.last() and not punch.end_at:
                errors.append(
                    _("Incomplete segment found: {type} started at {time} has no end time.").format(
                        type=punch.get_punch_type_display(),
                        time=punch.start_at.strftime("%H:%M")
                    )
                )
            
            last_punch = punch

        # 3. Check for excessive duration (Safety/Health rule)
        # Example: A single punch or total work exceeding 16 hours
        if timesheet.recorded_work > timedelta(hours=16):
            errors.append(_("Total recorded work exceeds 16 hours. Please verify for errors."))

        # 4. Check for break duration exceedance
        schedule = SchedulingService.get_expected_schedule(timesheet.employee, timesheet.register.date)
        if schedule and schedule.break_duration:
            if timesheet.recorded_break > schedule.break_duration:
                overtime_break = timesheet.recorded_break - schedule.break_duration
                errors.append(
                    _("Break exceedance detected: {duration} extra minutes.")
                    .format(duration=overtime_break.seconds // 60)
                )

        return errors

    @staticmethod
    def detect_orphaned_punches(employee, target_date) -> bool:
        """
        Detects if an employee has punches but no active EmploymentScheme.
        Useful for flagging payroll risks.
        """
        scheme = SchedulingService.get_active_scheme_for_date(employee, target_date)
        
        has_punches = TimePunch.objects.filter(
            timesheet__employee=employee,
            timesheet__register__date=target_date
        ).exists()

        return has_punches and not scheme

    @staticmethod
    def can_modify_attendance(timesheet: TimeSheet) -> bool:
        """
        Centralized check to see if a timesheet is editable.
        Considers both the Archive Lock and the DailyRegister finalization.
        """        
        # Rule 1: Archive Lock
        lock_date = AttendanceSettings.get_last_lock_date()
        if lock_date and timesheet.register.date <= lock_date:
            return False
            
        # Rule 2: Register Finalization
        if timesheet.register.is_finalized:
            # Note: We might allow HR to reopen a register, 
            # but by default, finalized means locked for calculation.
            return False

        return True

