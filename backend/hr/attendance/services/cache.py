"""
Attendance caching services.

Handles caching of attendance-related queries.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.attendance.models import (
    ShiftPolicy,
    ShiftDetail,
    EmploymentScheme,
    TimePunch,
    DailyRegister,
)


class AttendanceCacheService:
    """Cache operations for attendance module."""
    
    @staticmethod
    def get_shift_policy(policy_id):
        """Get shift policy (cached - stable)."""
        cache_key = generate_cache_key("hr:attendance:shift_policy", policy_id)
        policy = cache.get(cache_key)
        
        if policy is None:
            policy = ShiftPolicy.objects.get(id=policy_id)
            cache.set(cache_key, policy, timeout=60*60*24)  # 24h
        
        return policy
    
    @staticmethod
    def get_shift_details(policy):
        """Get shift details for policy."""
        if isinstance(policy, ShiftPolicy):
            policy_id = policy.id
        else:
            policy_id = policy
        
        cache_key = generate_cache_key("hr:attendance:shift_details", policy_id)
        details = cache.get(cache_key)
        
        if details is None:
            details = list(ShiftDetail.objects.filter(
                policy_id=policy_id
            ).order_by('shift_order'))
            
            cache.set(cache_key, details, timeout=60*60*24)  # 24h
        
        return details
    
    @staticmethod
    def get_employee_shifts(employee, period_start, period_end):
        """Get employee shifts for period."""
        cache_key = CacheKeys.employee_shifts(employee.id, period_start, period_end)
        shifts = cache.get(cache_key)
        
        if shifts is None:
            # Get employment scheme
            scheme = EmploymentScheme.objects.filter(
                employee=employee,
                effective_date__lte=period_start
            ).order_by('-effective_date').first()
            
            if scheme:
                shifts = AttendanceCacheService.get_shift_details(
                    scheme.shift_policy
                )
            else:
                shifts = []
            
            cache.set(cache_key, shifts, timeout=60*60*24)  # 24h
        
        return shifts
    
    @staticmethod
    def get_daily_register(employee, date):
        """Get daily register for employee (short cache)."""
        cache_key = CacheKeys.daily_register(employee.id, date)
        register = cache.get(cache_key)
        
        if register is None:
            register = DailyRegister.objects.filter(
                employee=employee,
                date=date
            ).first()
            
            if register:
                cache.set(cache_key, register, timeout=60*10)  # 10m
        
        return register
    
    @staticmethod
    def get_punches_for_date(employee, date):
        """Get all punches for employee on date (short cache)."""
        cache_key = generate_cache_key(
            "hr:attendance:punches", employee.id, date
        )
        punches = cache.get(cache_key)
        
        if punches is None:
            register = AttendanceCacheService.get_daily_register(employee, date)
            
            if register:
                punches = list(TimePunch.objects.filter(
                    register=register
                ).order_by('punch_time'))
            else:
                punches = []
            
            cache.set(cache_key, punches, timeout=60*5)  # 5m
        
        return punches
    
    @staticmethod
    def get_worked_hours(employee, date):
        """Calculate worked hours for employee on date."""
        cache_key = CacheKeys.worked_hours(employee.id, date)
        hours = cache.get(cache_key)
        
        if hours is None:
            punches = AttendanceCacheService.get_punches_for_date(
                employee, date
            )
            
            hours = sum(
                p.duration.total_seconds() / 3600
                for p in punches
                if p.duration
            )
            
            cache.set(cache_key, hours, timeout=60*10)  # 10m
        
        return hours
    
    @staticmethod
    def clear_employee_cache(employee):
        """Clear all attendance cache for employee."""
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        pattern = f"*hr:attendance*{employee.id}*"
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
