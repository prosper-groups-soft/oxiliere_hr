from __future__ import annotations
import logging
from datetime  import date, datetime, time, timedelta
from django.db import transaction
from django.utils import timezone

from hr.employees.models  import Employee
from hr.attendance.models import TimePunch, TimeSheet
from hr.attendance.enums  import TimeSheetStatus
from .attendance import AttendanceService
from .scheduling import SchedulingService


logger = logging.getLogger(__name__)


class AutoClosingService:
    """
    Nightly background service to handle forgotten punches and 
    mark unrecorded absences. Ensures data integrity for payroll.
    """

    @staticmethod
    @transaction.atomic
    def close_pending_punches(target_date: date):
        """
        Closes punches left open on target_date. 
        Smartly handles shift end times and overnight transitions.
        """
        open_punches = TimePunch.objects.filter(
            timesheet__register__date=target_date,
            end_at__isnull=True
        ).select_related('timesheet__employee', 'timesheet__register')

        for punch in open_punches:
            employee = punch.timesheet.employee
            schedule = SchedulingService.get_expected_schedule(employee, target_date)
            
            if schedule and schedule.end_time:
                # Logic: If end_time < start_time, it's a night shift ending the next day
                naive_end = datetime.combine(target_date, schedule.end_time)
                if schedule.end_time < schedule.start_time:
                    naive_end += timedelta(days=1)
                
                end_timestamp = timezone.make_aware(naive_end)
            else:
                # Fallback: close at the very end of the day
                naive_end = datetime.combine(target_date, time(23, 59, 59))
                end_timestamp = timezone.make_aware(naive_end)

            # Safety check: end_at cannot be before start_at
            if end_timestamp <= punch.start_at:
                # If the shift logic fails, we add a minimum duration (e.g., 1 min) 
                # to avoid negative durations
                end_timestamp = punch.start_at + timedelta(minutes=1)

            # Close and calculate duration
            punch.end_at = end_timestamp
            punch.duration = punch.end_at - punch.start_at
            punch.save()
            
            # Re-trigger total calculations (Recorded Work, Overtime, etc.)
            AttendanceService.compute_timesheet_totals(punch.timesheet)
            
            logger.info(f"Auto-closed punch for employee {employee.id} on {target_date}")

    @staticmethod
    @transaction.atomic
    def flag_unrecorded_absences(target_date: date):
        """
        Creates ABSENT timesheets for employees expected to work but who didn't punch.
        """
        register = AttendanceService.get_or_create_daily_register(target_date)
        
        # Performance: Use a subquery or set to find employees without timesheets
        existing_employee_ids = TimeSheet.objects.filter(
            register=register
        ).values_list('employee_id', flat=True)

        # We filter only active employees to avoid ghost absences
        active_employees = Employee.objects.filter(is_active=True).exclude(id__in=existing_employee_ids)

        for employee in active_employees:
            # Check if they were actually expected to work according to their scheme
            if SchedulingService.is_working_day(employee, target_date):
                TimeSheet.objects.create(
                    employee=employee,
                    register=register,
                    status=TimeSheetStatus.ABSENT,
                    recorded_work=timedelta(0),
                    recorded_break=timedelta(0),
                    shortfall=timedelta(0) # Will be updated by compute_timesheet_totals if needed
                )
                logger.info(f"Flagged absence for employee {employee.id} on {target_date}")

