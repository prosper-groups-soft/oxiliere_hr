"""
Jobs caching services.

Handles caching of job/organization structure queries.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.jobs.models import (
    JobFamily,
    Position,
    Department,
    EmploymentPosition,
)


class JobsCacheService:
    """Cache operations for jobs module."""
    
    @staticmethod
    def get_department(department_id):
        """Get department by ID (cached)."""
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
        """
        Get all departments.
        
        Args:
            flat: If True, return flat list. If False, return tree structure.
        
        Returns:
            List of departments
        """
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
        """Get job family by ID (cached)."""
        cache_key = generate_cache_key("hr:jobs:job_family", family_id)
        family = cache.get(cache_key)
        
        if family is None:
            family = JobFamily.objects.filter(id=family_id).first()
            
            if family:
                cache.set(cache_key, family, timeout=60*60*24)  # 24h
        
        return family
    
    @staticmethod
    def get_positions_by_family(family):
        """
        Get all positions for a job family (cached).
        
        Args:
            family: JobFamily instance or ID
        
        Returns:
            List of Position instances
        """
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
        """Get position by ID (cached)."""
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
        """Get positions in a department (cached)."""
        if isinstance(department, Department):
            department_id = department.id
        else:
            department_id = department
        
        cache_key = generate_cache_key(
            "hr:jobs:positions_dept", department_id
        )
        positions = cache.get(cache_key)
        
        if positions is None:
            positions = list(Position.objects.filter(
                department_id=department_id
            ).order_by('name'))
            
            cache.set(cache_key, positions, timeout=60*60*24)  # 24h
        
        return positions
    
    @staticmethod
    def get_current_position(employee):
        """
        Get current employment position for employee (cached).
        
        Args:
            employee: Employee instance
        
        Returns:
            EmploymentPosition instance or None
        """
        cache_key = CacheKeys.current_position(employee.id)
        position = cache.get(cache_key)
        
        if position is None:
            position = EmploymentPosition.objects.filter(
                employee=employee,
                is_current=True
            ).first()
            
            if position:
                cache.set(cache_key, position, timeout=60*60*12)  # 12h
        
        return position
    
    @staticmethod
    def get_employee_positions(employee):
        """Get all positions held by employee (cached)."""
        cache_key = generate_cache_key(
            "hr:jobs:employee_positions", employee.id
        )
        positions = cache.get(cache_key)
        
        if positions is None:
            positions = list(EmploymentPosition.objects.filter(
                employee=employee
            ).order_by('-effective_date'))
            
            cache.set(cache_key, positions, timeout=60*60*12)  # 12h
        
        return positions
    
    @staticmethod
    def clear_department_cache():
        """Clear department tree cache."""
        cache.delete(CacheKeys.department_tree())
        cache.delete(generate_cache_key("hr:jobs:departments", "flat"))
        cache.delete(generate_cache_key("hr:jobs:departments", "tree"))
    
    @staticmethod
    def clear_employee_position_cache(employee):
        """Clear position cache for employee."""
        cache.delete(CacheKeys.current_position(employee.id))
        cache.delete(generate_cache_key(
            "hr:jobs:employee_positions", employee.id
        ))
