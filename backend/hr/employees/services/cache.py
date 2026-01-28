"""
Employees caching services.

Handles caching of employee-related queries.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.employees.models import Employee


class EmployeeCacheService:
    """Cache operations for employees module."""
    
    @staticmethod
    def get_employee_by_matricule(matricule):
        """
        Get employee by matricule (frequently used - long cache).
        
        Args:
            matricule: Employee matricule/ID
        
        Returns:
            Employee instance or None
        """
        cache_key = CacheKeys.employee_matricule(matricule)
        employee = cache.get(cache_key)
        
        if employee is None:
            employee = Employee.objects.filter(
                matricule=matricule
            ).first()
            
            if employee:
                cache.set(cache_key, employee, timeout=60*60*24)  # 24h
        
        return employee
    
    @staticmethod
    def get_employee_by_id(employee_id):
        """Get employee by ID (cached)."""
        cache_key = generate_cache_key("hr:employees:id", employee_id)
        employee = cache.get(cache_key)
        
        if employee is None:
            employee = Employee.objects.filter(id=employee_id).first()
            
            if employee:
                cache.set(cache_key, employee, timeout=60*60*24)  # 24h
        
        return employee
    
    @staticmethod
    def get_active_employees(department=None):
        """
        Get all active employees (cached).
        
        Args:
            department: Optional Department instance to filter
        
        Returns:
            List of active Employee instances
        """
        department_id = None
        if department:
            department_id = department.id if hasattr(department, 'id') else department
        
        cache_key = CacheKeys.active_employees(department_id)
        employees = cache.get(cache_key)
        
        if employees is None:
            query = Employee.objects.filter(status='active')
            
            if department_id:
                query = query.filter(
                    current_position__department_id=department_id
                )
            
            employees = list(query.order_by('last_name', 'first_name'))
            cache.set(cache_key, employees, timeout=60*60*24)  # 24h
        
        return employees
    
    @staticmethod
    def get_all_employees(include_inactive=False):
        """Get all employees (cached)."""
        cache_key = generate_cache_key(
            "hr:employees:all", "with_inactive" if include_inactive else "active_only"
        )
        employees = cache.get(cache_key)
        
        if employees is None:
            query = Employee.objects.all()
            
            if not include_inactive:
                query = query.filter(status='active')
            
            employees = list(query.order_by('last_name', 'first_name'))
            cache.set(cache_key, employees, timeout=60*60*24)  # 24h
        
        return employees
    
    @staticmethod
    def get_employee_full_name(employee):
        """Get employee full name from cached instance."""
        if hasattr(employee, 'get_full_name'):
            return employee.get_full_name()
        
        return f"{employee.first_name} {employee.last_name}"
    
    @staticmethod
    def get_employee_family(employee):
        """Get employee family members (cached)."""
        cache_key = CacheKeys.employee_family(employee.id)
        family = cache.get(cache_key)
        
        if family is None:
            family = list(
                employee.family_members.all()
            )
            
            cache.set(cache_key, family, timeout=60*60*24)  # 24h
        
        return family
    
    @staticmethod
    def get_employee_documents(employee):
        """Get employee documents (cached)."""
        cache_key = generate_cache_key(
            "hr:employees:documents", employee.id
        )
        documents = cache.get(cache_key)
        
        if documents is None:
            documents = list(
                employee.documents.all()
            )
            
            cache.set(cache_key, documents, timeout=60*60*24)  # 24h
        
        return documents
    
    @staticmethod
    def clear_employee_cache(employee):
        """Clear all cache for an employee."""
        if isinstance(employee, Employee):
            employee_id = employee.id
            matricule = employee.matricule
        else:
            employee_id = employee
            matricule = None
        
        # Clear specific caches
        cache.delete(generate_cache_key("hr:employees:id", employee_id))
        
        if matricule:
            cache.delete(CacheKeys.employee_matricule(matricule))
        
        cache.delete(CacheKeys.employee_family(employee_id))
        cache.delete(generate_cache_key("hr:employees:documents", employee_id))
        
        # Clear list caches
        cache.delete(CacheKeys.active_employees())
        cache.delete(CacheKeys.active_employees("all"))
        cache.delete(generate_cache_key("hr:employees:all", "with_inactive"))
        cache.delete(generate_cache_key("hr:employees:all", "active_only"))
