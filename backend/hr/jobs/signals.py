from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from hr.jobs.models import (
    JobFamily,
    Position,
    OrgUnit,
    EmployeePositionHistory
)
from hr.jobs.services.cache import JobsCacheService


@receiver([post_save, post_delete], sender=OrgUnit)
def invalidate_org_unit_cache(sender, instance, **kwargs):
    """ Automatically clears organizational structure caches when org units change. """
    JobsCacheService.clear_org_unit_cache()


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
    """ Updates career history and organizational unit headcount caches. """
    JobsCacheService.clear_employee_position_cache(instance.employee)
    
    if instance.org_unit_id:
        JobsCacheService.clear_org_unit_positions_cache(instance.org_unit_id)

