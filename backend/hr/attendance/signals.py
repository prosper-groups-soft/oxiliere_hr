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
    """ Automatically clears relevant caches when attendance data changes. """
    
    employee = None
    if hasattr(instance, 'employee'):
        employee = instance.employee
    elif sender is TimePunch:
        employee = instance.timesheet.employee
    elif sender is TimeSheet:
        employee = instance.employee

    def clear_cache():
        # Clear global settings and registry lists
        AttendanceCacheService.clear_global_attendance_cache()
        
        # Clear employee-specific planning and status
        if employee:
            AttendanceCacheService.clear_employee_cache(employee)
            logger.debug(f"Individual cache invalidated for employee {employee.id}")

    # Ensure cache is cleared only after successful database commit
    transaction.on_commit(clear_cache)

