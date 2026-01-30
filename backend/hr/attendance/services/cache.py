import logging
from datetime          import date
from uuid              import UUID
from django.core.cache import cache
from django_redis      import get_redis_connection
from hr.services.cache_helpers import (
    generate_cache_key, 
    get_from_cache_or_call, 
    invalidate_cache_keys,
    invalidate_cache_prefix,
    CacheKeys
)
from hr.attendance.models import (
    ShiftPolicy,
    ShiftDetail,
    EmploymentScheme,
    TimePunch,
    DailyRegister,
    AttendanceSettings
)


logger = logging.getLogger(__name__)


class AttendanceCacheService:
    """
    High-performance cache operations for the attendance module.
    Optimizes schedule lookups, policy details, and employee-specific metrics.
    """

    @staticmethod
    def get_shift_policy(policy_id) -> ShiftPolicy:
        """
        Retrieves a shift policy from cache. 
        Policies are stable, so we use a long-lived 24h cache.
        """
        cache_key = generate_cache_key("hr:attendance:shift_policy", policy_id)
        policy = cache.get(cache_key)
        
        if policy is None:
            policy = ShiftPolicy.objects.get(id=policy_id)
            cache.set(cache_key, policy, timeout=60*60*24)  # 24h
        
        return policy
    
    @staticmethod
    def get_shift_details(policy: ShiftPolicy | UUID) -> list[ShiftDetail]:
        """
        Fetches all daily configurations (ShiftDetail) linked to a policy.
        
        This is a critical optimization for the SchedulingService: it loads the entire 
        weekly structure into memory at once, avoiding daily SQL queries in loops.
        """
        policy_id = policy.id if isinstance(policy, ShiftPolicy) else policy
        
        cache_key = generate_cache_key("hr:attendance:shift_details", policy_id)
        details = cache.get(cache_key)
        
        if details is None:
            # Load all 7 days in order and convert to list for pickling in cache
            details = list(ShiftDetail.objects.filter(
                policy_id=policy_id
            ).order_by('weekday')) # Ordering by weekday helps logic consistency
            
            cache.set(cache_key, details, timeout=60*60*24)  # 24h
        
        return details
    
    @staticmethod
    def get_employee_shifts(employee, period_start, period_end):
        """
        Retrieves the effective shifts for an employee during a specific period.
        Used primarily for UI displays and weekly planning views.
        """
        cache_key = CacheKeys.employee_shifts(employee.id, period_start, period_end)
        shifts = cache.get(cache_key)
        
        if shifts is None:
            # Locate the contractually active scheme at the start of the period
            scheme = EmploymentScheme.objects.filter(
                employee=employee,
                is_active=True,
                valid_from__lte=period_start
            ).order_by('-valid_from').first()
            
            if scheme:
                shifts = AttendanceCacheService.get_shift_details(scheme.policy)
            else:
                shifts = []
            
            cache.set(cache_key, shifts, timeout=60*60*24)  # 24h
        
        return shifts
    
    @staticmethod
    def get_daily_register(target_date: date) -> DailyRegister | None:
        """
        Accesses the master register for a specific date. 
        This record is shared across the company for that calendar day.
        """
        cache_key = generate_cache_key("hr:attendance:register:master", target_date)
        register = cache.get(cache_key)
        
        if register is None:
            register = DailyRegister.objects.filter(date=target_date).first()
            if register:
                cache.set(cache_key, register, timeout=60*60) # 1h cache
        
        return register
    
    @staticmethod
    def get_punches_for_date(employee, target_date: date):
        """
        Retrieves all raw time punches for an employee on a specific date.
        Uses a short 5-minute cache as punches happen in real-time.
        """
        cache_key = generate_cache_key("hr:attendance:punches", employee.id, target_date)
        punches = cache.get(cache_key)
        
        if punches is None:
            register = AttendanceCacheService.get_daily_register(target_date)
            if register:
                punches = list(TimePunch.objects.filter(
                    employee=employee,
                    register=register
                ).order_by('punch_time'))
            else:
                punches = []
            
            cache.set(cache_key, punches, timeout=60*5)  # 5m
        
        return punches
    
    @staticmethod
    def get_worked_hours(employee, target_date: date) -> float:
        """
        Calculates total hours worked based on punches.
        Result is cached for 10 minutes to support dashboard widgets.
        """
        cache_key = CacheKeys.worked_hours(employee.id, target_date)
        hours = cache.get(cache_key)
        
        if hours is None:
            punches = AttendanceCacheService.get_punches_for_date(employee, target_date)
            
            # Sum durations and convert seconds to decimal hours
            hours = sum(
                p.duration.total_seconds() / 3600
                for p in punches
                if p.duration
            )
            
            cache.set(cache_key, hours, timeout=60*10)  # 10m
        
        return hours
    
    @staticmethod
    def get_settings():
        """Returns the global attendance settings singleton."""
        return get_from_cache_or_call(
            "hr:attendance:settings",
            AttendanceSettings.load,
            timeout=60*60*24
        )

    @staticmethod
    def get_lock_date():
        """Returns the current payroll/attendance lock date."""
        return get_from_cache_or_call(
            "hr:attendance:lock_date",
            AttendanceSettings.get_last_lock_date,
            timeout=60*60*24
        )

    @staticmethod
    def clear_global_attendance_cache():
        """
        Invalidates everything global: 
        1. Low-level settings/dates (Your version)
        2. High-level API responses (My version)
        """
        # 1. Your constant keys (precise and fast)
        invalidate_cache_keys(
            "hr:attendance:settings", 
            "hr:attendance:lock_date"
        )
        
        # 2. My API patterns (Broad to ensure UI consistency)
        AttendanceCacheService.clear_api_cache_prefix("daily_register_list")
        AttendanceCacheService.clear_api_cache_prefix("period_lock_list")
        AttendanceCacheService.clear_api_cache_prefix("ts_list")
        AttendanceCacheService.clear_api_cache_prefix("policy_list")
        
        logger.info("Global attendance cache fully purged (Settings + API Lists).")
    
    @staticmethod
    def clear_api_cache_prefix(prefix: str):
        """Clears all cached API responses matching the given prefix."""
        invalidate_cache_prefix(prefix)
    
    @staticmethod
    def clear_employee_cache(employee):
        """
        Forcefully flushes all cached attendance data for a specific employee.
        
        Crucial when:
        1. An EmploymentScheme (policy) is changed.
        2. A manual override (ShiftAssignment) is added.
        3. A manual punch correction is made.
        
        Uses Redis SCAN for safe key deletion in production.
        """
        redis_conn = get_redis_connection("default")
        # Matches all keys containing the employee ID within the attendance namespace
        pattern = f"hr:attendance*:{employee.id}:*"
        
        # Iteratively fetch keys to avoid blocking the Redis event loop
        keys = list(redis_conn.scan_iter(match=pattern, count=100))
        
        if keys:
            redis_conn.delete(*keys)
        AttendanceCacheService.clear_api_cache_prefix(f"planning:{employee.id}")

