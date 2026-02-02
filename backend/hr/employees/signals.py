import logging
from django.dispatch import receiver
from django.db       import transaction
from django.db.models.signals import post_save, post_delete

from hr.employees.models import (
    Employee, 
    EmployeeAddress, 
    EmployeeDocument, 
    StatusHistory, 
    EmergencyContact, 
    EmployeeChild, 
    EmployeeEducation,
    WorkSite
)
from hr.employees.services.cache import EmployeeCacheService


logger = logging.getLogger(__name__)


# List of all models related to an employee that should trigger cache invalidation
EMPLOYEE_RELATED_MODELS = [
    Employee,
    EmployeeAddress,
    EmployeeDocument,
    StatusHistory,
    EmergencyContact,
    EmployeeChild,
    EmployeeEducation,
    WorkSite
]

@receiver([post_save, post_delete])
def invalidate_employee_cache_generic(sender, instance, **kwargs):
    """
    Generic signal handler for all employee-related models.
    Invalidates the specific employee cache and potentially global lists.
    """
    if sender not in EMPLOYEE_RELATED_MODELS:
        return

    def clear_cache():
        try:
            employee = None
            if isinstance(instance, Employee):
                employee = instance
            elif hasattr(instance, 'employee'):
                employee = instance.employee
                
            if employee:
                EmployeeCacheService.clear_employee_cache(employee)
                logger.debug(f"Cache invalidated for Employee {employee.matricule or employee.id} due to {sender.__name__} change.")
            elif isinstance(instance, WorkSite):
                # WorkSite change affects many employees, but we don't have a direct link 
                # to a single employee easily without reverse query.
                # For safety, we clear the employee list cache.
                EmployeeCacheService.clear_api_cache_prefix("employee_list")
                logger.debug(f"Employee list cache invalidated due to WorkSite change.")
                
        except Exception as e:
            logger.error(f"Error invalidating employee cache: {e}")

    # Debounce/Delay execution until after transaction commit
    transaction.on_commit(clear_cache)

