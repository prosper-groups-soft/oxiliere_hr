import logging
from django.dispatch import receiver
from django.db       import transaction
from django.db.models.signals import post_save, post_delete
from .models import (
    ShiftPolicy, 
    ShiftDetail, 
    EmploymentScheme, 
    TimePunch, 
    DailyRegister,
    TimeSheet,
    PeriodArchiveLock
)
from .services import AttendanceCacheService


logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=ShiftPolicy)
@receiver([post_save, post_delete], sender=ShiftDetail)
@receiver([post_save, post_delete], sender=EmploymentScheme)
@receiver([post_save, post_delete], sender=TimePunch)
@receiver([post_save, post_delete], sender=DailyRegister)
@receiver([post_save, post_delete], sender=TimeSheet)
@receiver([post_save, post_delete], sender=PeriodArchiveLock)
def invalidate_attendance_cache(sender, instance, **kwargs):
    """
    Triggered of various attendance-related model changes.
    """
    
    # 1. Resolving employee for individual cache (Schedule, Stats)
    employee = None
    if hasattr(instance, 'employee'):
        employee = instance.employee
    elif sender is TimePunch:
        # We go up via the timesheet
        employee = instance.timesheet.employee
    elif sender is TimeSheet:
        employee = instance.employee

    # 2. Defining the clearing logic
    def clear_cache():
        # A. Global clearing (Settings, Register & Lock API lists)
        # Done on structural changes (Policy, Lock, Register)
        # OR if a Punch/Sheet changes, as it impacts counts in lists
        AttendanceCacheService.clear_global_attendance_cache()
        
        # B. Employee-specific clearing
        if employee:
            AttendanceCacheService.clear_employee_cache(employee)
            logger.debug(f"Cache individuel invalidé pour l'employé {employee.id}")

    # 3. Execute safely after DB transaction commit
    transaction.on_commit(clear_cache)

