import logging
from __future__ import annotations
from datetime   import datetime, timedelta
from uuid       import UUID
from django.db  import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from hr.employees.models  import Employee
from hr.attendance.models import TimePunch, TimeSheet
from hr.attendance.enums  import PunchType
from .attendance import AttendanceService
from .validation import ValidationService 
# Cache integration
from .cache import AttendanceCacheService


logger = logging.getLogger(__name__)


class PunchService:
    """
    Service responsible for recording and managing raw time punches.
    Supports minimalist In/Out logic, Geofencing, and HR interventions.
    """

    @staticmethod
    @transaction.atomic
    def record_punch(
        actor_user, 
        timestamp: datetime, 
        punch_type: PunchType = PunchType.WORK, 
        is_manual: bool = False,
        employee_id: UUID = None,
        latitude: float = None,
        longitude: float = None,
    ) -> TimePunch | None:
        """
        Main entry point for punching. 
        Includes Geofencing validation before any record is created.
        """

        # 1. Target employee resolution
        if employee_id:
            target_employee = get_object_or_404(Employee, id=employee_id)
            is_manual = True 
        else:
            target_employee = get_object_or_404(Employee, user=actor_user)

        # 2. GEOGRAPHIC VALIDATION
        # GPS validation is only performed if it's not a manual entry (HR)
        if not is_manual:
            ValidationService.validate_geo_location(target_employee, latitude, longitude)

        # 3. TimeSheet resolution (Night shift management included)
        timesheet = PunchService.get_effective_timesheet_for_punch(target_employee, timestamp)

        # 4. Locking check
        # Ensure the date is not already archived or closed
        if not ValidationService.can_modify_attendance(timesheet):
            raise ValidationError("This period is locked and can no longer be modified.")

        # 5. Minimalist In/Out Logic
        punches = AttendanceCacheService.get_punches_for_date(target_employee, timesheet.register.date)
        open_punch_data = next((p for p in punches if p.end_at is None), None)

        if open_punch_data:
            # --- CLOCK-OUT ---
            open_punch = TimePunch.objects.get(id=open_punch_data.id)
            open_punch.end_at = timestamp
            # Coordinates are also stored during clock-out
            if latitude: open_punch.latitude = latitude
            if longitude: open_punch.longitude = longitude
            
            # Manual duration calculation (to avoid heavy model save() logic)
            open_punch.duration = open_punch.end_at - open_punch.start_at
            open_punch.save()
            
            punch_result = open_punch
        else:
            # --- CLOCK-IN ---
            punch_result = TimePunch.objects.create(
                timesheet=timesheet,
                punch_type=punch_type,
                start_at=timestamp,
                is_manual_entry=is_manual,
                latitude=latitude,
                longitude=longitude
            )

        # 6. Recalculation and Cache Clearing
        AttendanceService.compute_timesheet_totals(timesheet)
        AttendanceCacheService.clear_employee_cache(target_employee)
        
        logger.info(f"Punch recorded for employee {target_employee.id} on {timesheet.register.date}")
        
        return punch_result

    @staticmethod
    def get_effective_timesheet_for_punch(employee, timestamp: datetime) -> TimeSheet:
        """
        Resolves the correct TimeSheet, handling potential night shifts.
        """
        target_date = timestamp.date()
        yesterday = target_date - timedelta(days=1)
        
        # Night shift check: is there an open punch that started yesterday?
        yesterday_punches = AttendanceCacheService.get_punches_for_date(employee, yesterday)
        if any(p.end_at is None for p in yesterday_punches):
            register = AttendanceService.get_or_create_daily_register(yesterday)
            timesheet, _ = TimeSheet.objects.get_or_create(employee=employee, register=register)
            return timesheet

        register = AttendanceService.get_or_create_daily_register(target_date)
        timesheet, _ = TimeSheet.objects.get_or_create(employee=employee, register=register)
        
        logger.info(f"Resolved timesheet {timesheet.id} for punch at {timestamp} for employee {employee.id}")
        
        return timesheet

    @staticmethod
    @transaction.atomic
    def adjust_punch(
        punch: TimePunch, 
        start_at: datetime = None, 
        end_at: datetime = None, 
        punch_type: PunchType = None
    ) -> TimePunch:
        """
        Allows HR to manually fix a specific punch segment.
        Ensures the period is not locked before applying changes.
        """
        # 1. Security: Check if the timesheet is locked (Payroll closure)
        if not ValidationService.can_modify_attendance(punch.timesheet):
            raise ValidationError(
                _("This punch cannot be adjusted because the period is locked or finalized.")
            )

        # 2. Update fields
        if start_at:
            punch.start_at = start_at
        if end_at:
            punch.end_at = end_at
    
        if punch_type:
            punch.punch_type = punch_type        
            
        punch.is_manual_entry = True
        
        # 3. Recalculate duration
        if punch.start_at and punch.end_at:
            if punch.end_at < punch.start_at:
                raise ValidationError(_("End time cannot be before start time."))
            punch.duration = punch.end_at - punch.start_at
        else:
            punch.duration = timedelta(0)
            
        punch.save()

        # 4. Recalculation of daily totals (Work, Overtime, Status)
        AttendanceService.compute_timesheet_totals(punch.timesheet)
        
        # 5. Clear cache so the change is immediately visible
        AttendanceCacheService.clear_employee_cache(punch.timesheet.employee)
        
        logger.info(f"Punch {punch.id} adjusted by HR intervention.")
        
        return punch

    @staticmethod
    @transaction.atomic
    def delete_punch(punch: TimePunch):
        """
        Safely deletes a punch segment and updates the related timesheet.
        """
        timesheet = punch.timesheet
        employee = timesheet.employee

        # 1. Locking check
        if not ValidationService.can_modify_attendance(timesheet):
            raise ValidationError(
                _("This punch cannot be deleted because the period is locked or finalized.")
            )

        # 2. Soft deletion
        punch.delete()

        # 3. Recalculation of daily totals (Work, Overtime, Status)
        AttendanceService.compute_timesheet_totals(timesheet)
        
        # 4. Clear cache so the change is immediately visible
        AttendanceCacheService.clear_employee_cache(employee)
        
        logger.info(f"Punch {punch.id} deleted by HR intervention.")

