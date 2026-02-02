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
    """ Optimized cache operations for attendance policies, schedules, and metrics. """

    @staticmethod
    def get_shift_policy(policy_id) -> ShiftPolicy:
        """ Retrieves a shift policy from cache or database. """
        cache_key = generate_cache_key("hr:attendance:shift_policy", policy_id)
        policy = cache.get(cache_key)
        
        if policy is None:
            policy = ShiftPolicy.objects.get(id=policy_id)
            cache.set(cache_key, policy, timeout=60*60*24)
        
        return policy
    
    @staticmethod
    def get_shift_details(policy: ShiftPolicy | UUID) -> list[ShiftDetail]:
        """ Fetches full weekly configuration for a policy to avoid repeated SQL queries. """
        policy_id = policy.id if isinstance(policy, ShiftPolicy) else policy
        
        cache_key = generate_cache_key("hr:attendance:shift_details", policy_id)
        details = cache.get(cache_key)
        
        if details is None:
            details = list(ShiftDetail.objects.filter(
                policy_id=policy_id
            ).order_by('weekday'))
            
            cache.set(cache_key, details, timeout=60*60*24)
        
        return details
    
    @staticmethod
    def get_employee_shifts(employee, period_start, period_end):
        """ Retrieves effective shifts for an employee during a specific period. """
        cache_key = CacheKeys.employee_shifts(employee.id, period_start, period_end)
        shifts = cache.get(cache_key)
        
        if shifts is None:
            scheme = EmploymentScheme.objects.filter(
                employee=employee,
                is_active=True,
                valid_from__lte=period_start
            ).order_by('-valid_from').first()
            
            if scheme:
                shifts = AttendanceCacheService.get_shift_details(scheme.policy)
            else:
                shifts = []
            
            cache.set(cache_key, shifts, timeout=60*60*24)
        
        return shifts
    
    @staticmethod
    def get_daily_register(target_date: date) -> DailyRegister | None:
        """ Accesses the consolidated daily registry for a specific date. """
        cache_key = generate_cache_key("hr:attendance:register:master", target_date)
        register = cache.get(cache_key)
        
        if register is None:
            register = DailyRegister.objects.filter(date=target_date).first()
            if register:
                cache.set(cache_key, register, timeout=60*60)
        
        return register
    
    @staticmethod
    def get_punches_for_date(employee, target_date: date):
        """ Retrieves raw time punches for an employee on a specific date. """
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
            
            cache.set(cache_key, punches, timeout=60*5)
        
        return punches
    
    @staticmethod
    def get_worked_hours(employee, target_date: date) -> float:
        """ Calculates and caches total hours worked for dashboard metrics. """
        cache_key = CacheKeys.worked_hours(employee.id, target_date)
        hours = cache.get(cache_key)
        
        if hours is None:
            punches = AttendanceCacheService.get_punches_for_date(employee, target_date)
            hours = sum(
                p.duration.total_seconds() / 3600
                for p in punches
                if p.duration
            )
            cache.set(cache_key, hours, timeout=60*10)
        
        return hours
    
    @staticmethod
    def get_settings():
        """ Retrieves global attendance settings from cache. """
        return get_from_cache_or_call(
            "hr:attendance:settings",
            AttendanceSettings.load,
            timeout=60*60*24
        )

    @staticmethod
    def get_lock_date():
        """ Retrieves the current administrative lock date. """
        return get_from_cache_or_call(
            "hr:attendance:lock_date",
            AttendanceSettings.get_last_lock_date,
            timeout=60*60*24
        )

    @staticmethod
    def clear_global_attendance_cache():
        """ Invalidates all global attendance settings and registry lists. """
        invalidate_cache_keys(
            "hr:attendance:settings", 
            "hr:attendance:lock_date"
        )
        
        AttendanceCacheService.clear_api_cache_prefix("daily_register_list")
        AttendanceCacheService.clear_api_cache_prefix("period_lock_list")
        AttendanceCacheService.clear_api_cache_prefix("ts_list")
        AttendanceCacheService.clear_api_cache_prefix("policy_list")
        AttendanceCacheService.clear_api_cache_prefix("working_day_check")
        
        logger.info("Global attendance cache purged.")
    
    @staticmethod
    def clear_api_cache_prefix(prefix: str):
        """ Clears cached API responses matching the given prefix. """
        invalidate_cache_prefix(prefix)
    
    @staticmethod
    def clear_employee_cache(employee):
        """ Flushes all attendance-related cache entries for a specific employee. """
        redis_conn = get_redis_connection("default")
        pattern = f"hr:attendance*:{employee.id}:*"
        
        keys = list(redis_conn.scan_iter(match=pattern, count=100))
        
        if keys:
            redis_conn.delete(*keys)
        AttendanceCacheService.clear_api_cache_prefix(f"planning:{employee.id}")

