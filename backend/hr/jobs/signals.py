from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from hr.jobs.models import (
    JobFamily,
    Position,
    Department,
    EmployeePositionHistory
)
from hr.jobs.services.cache import JobsCacheService


@receiver([post_save, post_delete], sender=Department)
def invalidate_department_cache(sender, instance, **kwargs):
    """ Automatically clears organizational structure caches when departments change. """
    JobsCacheService.clear_department_cache()


@receiver([post_save, post_delete], sender=JobFamily)
def invalidate_job_family_cache(sender, instance, **kwargs):
    """ Clears cached job family data and associated positions. """
    JobsCacheService.clear_job_family_cache(instance.id)


@receiver([post_save, post_delete], sender=Position)
def invalidate_position_cache(sender, instance, **kwargs):
    """ Invalidates position-specific caches. """
    JobsCacheService.clear_position_cache(
        instance.id, 
        family_id=instance.job_family_id
    )


@receiver([post_save, post_delete], sender=EmployeePositionHistory)
def invalidate_employee_position_history(sender, instance, **kwargs):
    """ Updates career history and departmental headcount caches. """
    JobsCacheService.clear_employee_position_cache(instance.employee)
    
    if instance.department_id:
        JobsCacheService.clear_department_positions_cache(instance.department_id)

