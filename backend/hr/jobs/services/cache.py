import logging
from django.core.cache import cache
from django_redis      import get_redis_connection
from hr.services.cache_helpers import (
    generate_cache_key, 
    CacheKeys, 
    invalidate_cache_pattern
)
from hr.jobs.models import (
    JobFamily,
    Position,
    OrgUnit,
    EmployeePositionHistory,
)


logger = logging.getLogger(__name__)


class JobsCacheService:
    """ Centralized cache management for organizational structure and job data. """
    
    redis_conn = get_redis_connection("default")
    
    @staticmethod
    def get_org_unit(unit_id):
        """ Retrieves a cached organizational unit instance. """
        cache_key = generate_cache_key("hr:jobs:orgunit", unit_id)
        unit = cache.get(cache_key)
        
        if unit is None:
            unit = OrgUnit.objects.filter(
                id=unit_id
            ).first()
            
            if unit:
                cache.set(cache_key, unit, timeout=60*60*24)  # 24h
        
        return unit
    
    @staticmethod
    def get_org_tree():
        """
        Get full organizational tree (stable org structure - long cache).
        
        Returns:
            List of root units with children
        """
        cache_key = CacheKeys.org_tree()
        tree = cache.get(cache_key)
        
        if tree is None:
            # Build org unit hierarchy
            tree = list(OrgUnit.objects.filter(
                parent=None
            ).prefetch_related('sub_units').order_by('name'))
            
            cache.set(cache_key, tree, timeout=60*60*24)  # 24h
        
        return tree
    
    @staticmethod
    def get_all_org_units(flat=False):
        """ Retrieves a list of all org units, either flat or as a hierarchy. """
        cache_key = generate_cache_key(
            "hr:jobs:org_units", "flat" if flat else "tree"
        )
        org_units = cache.get(cache_key)
        
        if org_units is None:
            if flat:
                org_units = list(OrgUnit.objects.all().order_by('name'))
            else:
                org_units = JobsCacheService.get_org_tree()
            
            cache.set(cache_key, org_units, timeout=60*60*24)  # 24h
        
        return org_units
    
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
    def get_positions_by_org_unit(org_unit):
        """ Retrieves all positions currently active within a specific org unit. """
        if isinstance(org_unit, OrgUnit):
            org_unit_id = org_unit.id
        else:
            org_unit_id = org_unit
        
        cache_key = generate_cache_key(
            "hr:jobs:positions_unit", org_unit_id
        )
        positions = cache.get(cache_key)
        
        if positions is None:
            # We fetch positions that are currently active in this org unit
            # This requires a subquery or join through EmployeePositionHistory
            position_ids = EmployeePositionHistory.objects.filter(
                org_unit_id=org_unit_id,
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
    def clear_org_unit_cache():
        """ Invalidates all org unit-related caches. """
        cache.delete(CacheKeys.org_tree())
        cache.delete(generate_cache_key("hr:jobs:org_units", "flat"))
        cache.delete(generate_cache_key("hr:jobs:org_units", "tree"))
        
        # Also clear cache_api_response keys for organization endpoints
        JobsCacheService.clear_org_tree_api_cache()
    
    @staticmethod
    def clear_org_tree_api_cache():
        """ Clear cache_api_response keys for org tree and unit list endpoints. """
        # Pattern: :1:org_tree:shared:/api/organization/tree
        patterns = [
            "*:org_tree:*",
            "*:unit_list:*",
        ]
        for pattern in patterns:
            keys = JobsCacheService.redis_conn.keys(pattern)
            if keys:
                JobsCacheService.redis_conn.delete(*keys)
                logger.info(f"[Cache] Cleared {len(keys)} org API cache keys for pattern: {pattern}")
            else:
                logger.info(f"[Cache] No org API cache keys found for pattern: {pattern}")

    @staticmethod
    def clear_employee_list_api_cache():
        """ Clear cache_api_response keys for employee list endpoint. """
        patterns = [
            "*:employee_list:*",
        ]
        for pattern in patterns:
            keys = JobsCacheService.redis_conn.keys(pattern)
            if keys:
                JobsCacheService.redis_conn.delete(*keys)
                logger.info(f"[Cache] Cleared {len(keys)} employee API cache keys for pattern: {pattern}")
            else:
                logger.info(f"[Cache] No employee API cache keys found for pattern: {pattern}")
    
    @staticmethod
    def clear_org_unit_positions_cache(org_unit_id):
        """ Invalidates the list of positions for a specific org unit. """
        cache.delete(generate_cache_key("hr:jobs:positions_unit", org_unit_id))

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
    def clear_job_families_list_cache():
        """ Invalidates the job families list cache. """
        invalidate_cache_pattern("*:job_families_list*")
        logger.info("[Cache] Cleared job families list cache")

    @staticmethod
    def clear_position_cache(position_id, family_id=None):
        """ Invalidates cache entries for a specific position. """
        cache.delete(generate_cache_key("hr:jobs:position", position_id))
        if family_id:
            cache.delete(CacheKeys.positions_by_family(family_id))

    @staticmethod
    def clear_seniority_levels_cache():
        """ Invalidates all seniority levels cache entries. """
        # Clear cache_api_response keys for seniority levels endpoint
        patterns = [
            "*:seniority_levels:*",
            "*seniority_levels*",  # Pattern utilisé par cache_api_response
        ]
        for pattern in patterns:
            keys = JobsCacheService.redis_conn.keys(pattern)
            if keys:
                JobsCacheService.redis_conn.delete(*keys)
                logger.info(f"[Cache] Cleared {len(keys)} seniority levels cache keys for pattern: {pattern}")
            else:
                logger.info(f"[Cache] No seniority levels cache keys found for pattern: {pattern}")

