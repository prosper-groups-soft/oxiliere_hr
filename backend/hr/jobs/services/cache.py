from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.jobs.models import (
    JobFamily,
    Position,
    Department,
    Department,
    EmployeePositionHistory,
)


class JobsCacheService:
    """ Centralized cache management for organizational structure and job data. """
    
    @staticmethod
    def get_department(department_id):
        """ Retrieves a cached department instance. """
        cache_key = generate_cache_key("hr:jobs:department", department_id)
        department = cache.get(cache_key)
        
        if department is None:
            department = Department.objects.filter(
                id=department_id
            ).first()
            
            if department:
                cache.set(cache_key, department, timeout=60*60*24)  # 24h
        
        return department
    
    @staticmethod
    def get_department_tree():
        """
        Get full department tree (stable org structure - long cache).
        
        Returns:
            List of root departments with children
        """
        cache_key = CacheKeys.department_tree()
        tree = cache.get(cache_key)
        
        if tree is None:
            # Build department hierarchy
            tree = list(Department.objects.filter(
                parent=None
            ).prefetch_related('children').order_by('name'))
            
            cache.set(cache_key, tree, timeout=60*60*24)  # 24h
        
        return tree
    
    @staticmethod
    def get_all_departments(flat=False):
        """ Retrieves a list of all departments, either flat or as a hierarchy. """
        cache_key = generate_cache_key(
            "hr:jobs:departments", "flat" if flat else "tree"
        )
        departments = cache.get(cache_key)
        
        if departments is None:
            if flat:
                departments = list(Department.objects.all().order_by('name'))
            else:
                departments = JobsCacheService.get_department_tree()
            
            cache.set(cache_key, departments, timeout=60*60*24)  # 24h
        
        return departments
    
    @staticmethod
    def get_job_family(family_id):
        """ Retrieves a cached job family instance. """
        cache_key = generate_cache_key("hr:jobs:job_family", family_id)
        family = cache.get(cache_key)
        
        if family is None:
            family = JobFamily.objects.filter(id=family_id).first()
            
            if family:
                cache.set(cache_key, family, timeout=60*60*24)  # 24h
        
        return family
    
    @staticmethod
    def get_positions_by_family(family):
        """ Retrieves all positions associated with a specific job family. """
        if isinstance(family, JobFamily):
            family_id = family.id
        else:
            family_id = family
        
        cache_key = CacheKeys.positions_by_family(family_id)
        positions = cache.get(cache_key)
        
        if positions is None:
            positions = list(Position.objects.filter(
                family_id=family_id
            ).order_by('name'))
            
            cache.set(cache_key, positions, timeout=60*60*24)  # 24h
        
        return positions
    
    @staticmethod
    def get_position(position_id):
        """ Retrieves a cached position instance. """
        cache_key = generate_cache_key("hr:jobs:position", position_id)
        position = cache.get(cache_key)
        
        if position is None:
            position = Position.objects.filter(
                id=position_id
            ).first()
            
            if position:
                cache.set(cache_key, position, timeout=60*60*24)  # 24h
        
        return position
    
    @staticmethod
    def get_positions_by_department(department):
        """ Retrieves all positions currently active within a specific department. """
        if isinstance(department, Department):
            department_id = department.id
        else:
            department_id = department
        
        cache_key = generate_cache_key(
            "hr:jobs:positions_dept", department_id
        )
        positions = cache.get(cache_key)
        
        if positions is None:
            # We fetch positions that are currently active in this department
            # This requires a subquery or join through EmployeePositionHistory
            position_ids = EmployeePositionHistory.objects.filter(
                department_id=department_id,
                is_current=True
            ).values_list('position_id', flat=True).distinct()
            
            positions = list(Position.objects.filter(
                id__in=position_ids
            ).order_by('name'))
            
            cache.set(cache_key, positions, timeout=60*60*24)  # 24h
        
        return positions
    
    @staticmethod
    def get_current_position(employee):
        """ Retrieves the employee's current active role. """
        cache_key = CacheKeys.current_position(employee.id)
        position = cache.get(cache_key)
        
        if position is None:
            position = EmployeePositionHistory.objects.filter(
                employee=employee,
                is_current=True
            ).first()
            
            if position:
                cache.set(cache_key, position, timeout=60*60*12)  # 12h
        
        return position
    
    @staticmethod
    def get_employee_positions(employee):
        """ Retrieves the complete career history for an employee. """
        cache_key = generate_cache_key(
            "hr:jobs:employee_positions", employee.id
        )
        positions = cache.get(cache_key)
        
        if positions is None:
            positions = list(EmployeePositionHistory.objects.filter(
                employee=employee
            ).order_by('-start_date'))
            
            cache.set(cache_key, positions, timeout=60*60*12)  # 12h
        
        return positions
    
    @staticmethod
    def clear_department_cache():
        """ Invalidates all department-related caches. """
        cache.delete(CacheKeys.department_tree())
        cache.delete(generate_cache_key("hr:jobs:departments", "flat"))
        cache.delete(generate_cache_key("hr:jobs:departments", "tree"))
    
    @staticmethod
    def clear_department_positions_cache(department_id):
        """ Invalidates the list of positions for a specific department. """
        cache.delete(generate_cache_key("hr:jobs:positions_dept", department_id))

    @staticmethod
    def clear_employee_position_cache(employee):
        """ Invalidates cache entries for an employee's career records. """
        cache.delete(CacheKeys.current_position(employee.id))
        cache.delete(generate_cache_key(
            "hr:jobs:employee_positions", employee.id
        ))

    @staticmethod
    def clear_job_family_cache(family_id):
        """ Invalidates cache entries for a job family and its positions. """
        cache.delete(generate_cache_key("hr:jobs:job_family", family_id))
        cache.delete(CacheKeys.positions_by_family(family_id))

    @staticmethod
    def clear_position_cache(position_id, family_id=None):
        """ Invalidates cache entries for a specific position. """
        cache.delete(generate_cache_key("hr:jobs:position", position_id))
        if family_id:
            cache.delete(CacheKeys.positions_by_family(family_id))
