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
    """ Background service for automated attendance reconciliation and integrity. """

    @staticmethod
    @transaction.atomic
    def close_pending_punches(target_date: date):
        """ Closes forgotten punches using shift templates to estimate end times. """
        open_punches = TimePunch.objects.filter(
            timesheet__register__date=target_date,
            end_at__isnull=True
        ).select_related('timesheet__employee', 'timesheet__register')

        for punch in open_punches:
            employee = punch.timesheet.employee
            schedule = SchedulingService.get_expected_schedule(employee, target_date)
            
            if schedule and schedule.end_time:
                naive_end = datetime.combine(target_date, schedule.end_time)
                if schedule.end_time < schedule.start_time:
                    naive_end += timedelta(days=1)
                
                end_timestamp = timezone.make_aware(naive_end)
            else:
                naive_end = datetime.combine(target_date, time(23, 59, 59))
                end_timestamp = timezone.make_aware(naive_end)

            if end_timestamp <= punch.start_at:
                end_timestamp = punch.start_at + timedelta(minutes=1)

            punch.end_at = end_timestamp
            punch.duration = punch.end_at - punch.start_at
            punch.save()
            
            AttendanceService.compute_timesheet_totals(punch.timesheet)
            
            logger.info(f"Auto-closed punch for employee {employee.id} on {target_date}")

    @staticmethod
    @transaction.atomic
    def flag_unrecorded_absences(target_date: date):
        """ Records absences for employees who were scheduled but did not punch. """
        register = AttendanceService.get_or_create_daily_register(target_date)
        
        existing_employee_ids = TimeSheet.objects.filter(
            register=register
        ).values_list('employee_id', flat=True)

        active_employees = Employee.objects.filter(is_active=True).exclude(id__in=existing_employee_ids)

        for employee in active_employees:
            if SchedulingService.is_working_day(employee, target_date):
                TimeSheet.objects.create(
                    employee=employee,
                    register=register,
                    status=TimeSheetStatus.ABSENT,
                    recorded_work=timedelta(0),
                    recorded_break=timedelta(0),
                    shortfall=timedelta(0)
                )
                logger.info(f"Flagged absence for employee {employee.id} on {target_date}")

