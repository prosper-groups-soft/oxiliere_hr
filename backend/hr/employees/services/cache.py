from django.core.cache         import cache
from hr.services.cache_helpers import (
    generate_cache_key, 
    CacheKeys, 
    invalidate_cache_prefix,
    invalidate_cache_pattern
)
from hr.employees.models import Employee


class EmployeeCacheService:
    """ Caching performance layer for employees module. """
    
    @staticmethod
    def get_employee_by_matricule(matricule):
        """ Retrieves employee from cache or DB by staff ID. """
        cache_key = CacheKeys.employee_matricule(matricule)
        employee = cache.get(cache_key)
        
        if employee is None:
            employee = Employee.objects.filter(matricule=matricule).first()
            if employee:
                cache.set(cache_key, employee, timeout=60*60*24)
        
        return employee
    
    @staticmethod
    def get_employee_by_id(employee_id):
        """ Retrieves employee from cache or DB by internal ID. """
        cache_key = generate_cache_key("hr:employees:id", employee_id)
        employee = cache.get(cache_key)
        
        if employee is None:
            employee = Employee.objects.filter(id=employee_id).first()
            if employee:
                cache.set(cache_key, employee, timeout=60*60*24)
        
        return employee
    
    @staticmethod
    def get_active_employees():
        """ Returns all currently active personnel from cache. """
        cache_key = CacheKeys.active_employees()
        employees = cache.get(cache_key)
        
        if employees is None:
            employees = list(Employee.objects.filter(is_active=True).order_by('last_name', 'first_name'))
            cache.set(cache_key, employees, timeout=60*60*24)
        
        return employees
    
    @staticmethod
    def get_all_employees(include_inactive=False):
        """ Returns complete headcount from cache. """
        cache_key = generate_cache_key(
            "hr:employees:all", "with_inactive" if include_inactive else "active_only"
        )
        employees = cache.get(cache_key)
        
        if employees is None:
            query = Employee.objects.all()
            if not include_inactive:
                query = query.filter(is_active=True)
            
            employees = list(query.order_by('last_name', 'first_name'))
            cache.set(cache_key, employees, timeout=60*60*24)
        
        return employees
    
    @staticmethod
    def get_employee_full_name(employee):
        """ Formats complete name for display. """
        return f"{employee.first_name} {employee.last_name}"
    
    @staticmethod
    def get_employee_children(employee):
        """ Retrieves dependent children for benefits. """
        cache_key = CacheKeys.employee_family(employee.id)
        children = cache.get(cache_key)
        
        if children is None:
            children = list(employee.children.all())
            cache.set(cache_key, children, timeout=60*60*24)
        
        return children
    
    @staticmethod
    def get_employee_documents(employee):
        """ Retrieves employee credentials and files. """
        cache_key = generate_cache_key("hr:employees:documents", employee.id)
        documents = cache.get(cache_key)
        
        if documents is None:
            documents = list(employee.documents.all())
            cache.set(cache_key, documents, timeout=60*60*24)
        
        return documents
    
    @staticmethod
    def clear_api_cache_prefix(prefix: str):
        """ Invalidates all API responses with specified prefix. """
        invalidate_cache_prefix(prefix)

    @staticmethod
    def clear_employee_cache(employee):
        """ Purges all cached records for a specific employee. """
        if isinstance(employee, Employee):
            employee_id = employee.id
            matricule = employee.matricule
        else:
            employee_id = employee
            matricule = None
        
        # Data Cache
        cache.delete(generate_cache_key("hr:employees:id", employee_id))
        if matricule:
            cache.delete(CacheKeys.employee_matricule(matricule))
        
        cache.delete(CacheKeys.employee_family(employee_id))
        cache.delete(generate_cache_key("hr:employees:documents", employee_id))
        
        # Global Lists
        cache.delete(CacheKeys.active_employees())
        cache.delete(generate_cache_key("hr:employees:all", "with_inactive"))
        cache.delete(generate_cache_key("hr:employees:all", "active_only"))

        # API Cache
        invalidate_cache_pattern(f"employee_detail:shared:/api/employees/{employee_id}")
        EmployeeCacheService.clear_api_cache_prefix("employee_list")

