import logging
from functools import wraps
from django.core.cache import cache
from django_redis import get_redis_connection


logger = logging.getLogger(__name__)


def cache_query(timeout=None, key_prefix="", key_args=None):
    """
    Decorator to cache querysets results.
    
    Args:
        timeout: Cache timeout in seconds (default: 3600)
        key_prefix: Prefix for cache key (default: function name)
        key_args: Tuple of argument indices to include in cache key
                 (e.g., (1, 2) to include args 1 and 2 after self)
    
    Example:
        @cache_query(timeout=60*60, key_args=(1, 2))
        def get_employee_contract(self, employee_id, date):
            return EmployeeContract.objects.get(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            key_parts = [prefix]
            
            # Add args to key if specified
            if key_args:
                for idx in key_args:
                    if idx < len(args):
                        key_parts.append(str(args[idx]))
            
            # Add kwargs to key
            if kwargs:
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout or 60*60)
            
            return result
        
        return wrapper
    return decorator


def cache_model_list(timeout=None, key_prefix=""):
    """
    Decorator specifically for caching model querysets.
    Converts queryset to list automatically.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Cache key prefix
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = prefix
            
            # Add kwargs to key
            if kwargs:
                for k, v in sorted(kwargs.items()):
                    cache_key += f":{k}={v}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute and convert to list
            result = list(func(*args, **kwargs))
            cache.set(cache_key, result, timeout or 60*60)
            
            return result
        
        return wrapper
    return decorator


def cache_api_response(timeout=60*5, key_prefix="api_cache", user_specific=True):
    """
    Decorator to cache API responses.
    
    Args:
        timeout: Time in seconds.
        key_prefix: Prefix for the key.
        user_specific: If False, the cache is shared between all users 
                       (ideal for global lists/settings).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Intelligent detection of the request object
            request = None
            
            # Case 1: First argument is the request (simple function)
            if args and hasattr(args[0], 'get_full_path'):
                request = args[0]
            # Case 2: First argument is 'self' (Ninja Extra Controller)
            elif args and hasattr(args[0], 'context') and hasattr(args[0].context, 'request'):
                request = args[0].context.request
            # Case 3: Search in kwargs (fallback)
            else:
                request = kwargs.get('request')

            if not request:
                raise AttributeError(
                    f"Cache decorator: Could not find HttpRequest object in "
                    f"arguments or controller context for {func.__name__}"
                )

            # Construction of the key
            path = request.get_full_path()
            
            if user_specific and request.user.is_authenticated:
                user_id = request.user.id
                cache_key = f"{key_prefix}:{user_id}:{path}"
            else:
                # Shared key: Fewer keys in Redis, easier to invalidate
                cache_key = f"{key_prefix}:shared:{path}"
            
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data
            
            response_data = func(*args, **kwargs)
            cache.set(cache_key, response_data, timeout)
            
            return response_data
        return wrapper
    return decorator


def generate_cache_key(*parts):
    """
    Generate a cache key from multiple parts.
    
    Example:
        key = generate_cache_key("hr:payroll", employee_id, "contract", date)
        # Result: hr:payroll:123:contract:2026-01-28
    """
    return ":".join(str(p) for p in parts if p is not None)


def get_from_cache_or_call(cache_key, func, *args, timeout=None, **kwargs):
    """
    Get value from cache or call function if not cached.
    
    Args:
        cache_key: Key to use for caching
        func: Function to call if cache miss
        args: Arguments for function
        timeout: Cache timeout
        kwargs: Keyword arguments for function
    
    Returns:
        Cached or freshly computed value
    """
    result = cache.get(cache_key)
    if result is not None:
        return result
    
    result = func(*args, **kwargs)
    cache.set(cache_key, result, timeout or 60*60)
    
    return result


def invalidate_cache_keys(*keys):
    """
    Invalidate multiple cache keys.
    
    Example:
        invalidate_cache_keys(
            "hr:payroll:contract:123",
            "hr:leaves:balance:123:2026"
        )
    """
    cache.delete_many(keys)


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    
    WARNING: This operation is slow on Redis. Use sparingly.
    
    Args:
        pattern: Pattern to match (with wildcards)
    
    Example:
        invalidate_cache_pattern("hr:payroll:contract:123:*")
    """    
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys(f"*{pattern}*")
    if keys:
        redis_conn.delete(*keys)


def invalidate_cache_prefix(prefix: str):
    """
    Delete all cache keys starting with the given prefix.
    Useful for clearing multi-user API caches.
    """
    redis_conn = get_redis_connection("default")
    # We iteratively scan and delete matching keys
    cursor = '0'
    while cursor != 0:
        cursor, keys = redis_conn.scan(cursor=cursor, match=f"{prefix}:*", count=1000)
        if keys:
            redis_conn.delete(*keys)
    logger.info(f"Cache pattern cleared: {prefix}:*")


def clear_all_cache():
    """Clear all cache (use with caution)."""
    cache.clear()


class CachedProperty:
    """
    Cached property decorator similar to @cached_property
    but with custom timeout.
    
    Example:
        class Service:
            @CachedProperty(timeout=60*60)
            def configuration(self):
                return PayrollConfiguration.objects.first()
    """
    def __init__(self, func, timeout=None):
        self.func = func
        self.timeout = timeout or 60*60
        self.__doc__ = func.__doc__
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        # Generate cache key
        cache_key = f"{objtype.__name__}:{self.func.__name__}"
        
        # Try to get from cache
        value = cache.get(cache_key)
        if value is not None:
            return value
        
        # Compute and cache
        value = self.func(obj)
        cache.set(cache_key, value, self.timeout)
        
        return value


def cache_invalidator(*models):
    """
    Create a function that invalidates cache for specific models.
    
    Returns:
        Function that invalidates cache
    
    Example:
        from django.db.models.signals import post_save
        
        @receiver(post_save, sender=PayrollConfiguration)
        def invalidate_config(sender, instance, **kwargs):
            invalidate_payroll_config()
        
        invalidate_payroll_config = cache_invalidator(PayrollConfiguration)
    """
    def invalidator(*cache_keys):
        """Invalidate cache keys for models"""
        invalidate_cache_keys(*cache_keys)
    
    return invalidator


def get_cache_stats():
    """
    Get cache statistics from Redis.
    
    Returns:
        Dict with cache stats (keys count, memory, hit rate, etc.)
    """
    try:
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        total_keys = redis_conn.dbsize()
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total_requests = hits + misses
        
        return {
            'total_keys': total_keys,
            'memory_mb': info.get('used_memory', 0) / 1024 / 1024,
            'memory_human': info.get('used_memory_human', 'N/A'),
            'hits': hits,
            'misses': misses,
            'hit_rate': (hits / total_requests * 100) if total_requests > 0 else 0,
            'evictions': info.get('evicted_keys', 0),
            'connected_clients': info.get('connected_clients', 0),
        }
    except Exception as e:
        return {'error': str(e)}


def get_cache_keys_pattern(pattern):
    """
    Get all cache keys matching a pattern.
    List of matching keys.
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        return redis_conn.keys(f"*{pattern}*")
    except Exception as e:
        return {'error': str(e)}


# Helper for common cache keys
class CacheKeys:
    """Cache key constants and builders."""
    
    # PAYROLL
    @staticmethod
    def payroll_config():
        return generate_cache_key("hr:payroll:config")
    
    @staticmethod
    def payroll_contract(employee_id, date=None):
        return generate_cache_key("hr:payroll:contract", employee_id, date)
    
    @staticmethod
    def payroll_run(payroll_run_id):
        return generate_cache_key("hr:payroll:run", payroll_run_id)
    
    @staticmethod
    def salary_advance(employee_id):
        return generate_cache_key("hr:payroll:advance", employee_id)
    
    # LEAVES
    @staticmethod
    def leave_balance(employee_id, year):
        return generate_cache_key("hr:leaves:balance", employee_id, year)
    
    @staticmethod
    def leave_policy(policy_id):
        return generate_cache_key("hr:leaves:policy", policy_id)
    
    @staticmethod
    def seniority_rules(policy_id):
        return generate_cache_key("hr:leaves:rules", policy_id)
    
    # ATTENDANCE
    @staticmethod
    def employee_shifts(employee_id, period_start, period_end):
        return generate_cache_key("hr:attendance:shifts", employee_id, period_start, period_end)
    
    @staticmethod
    def worked_hours(employee_id, date):
        return generate_cache_key("hr:attendance:hours", employee_id, date)
    
    @staticmethod
    def daily_register(employee_id, date):
        return generate_cache_key("hr:attendance:register", employee_id, date)
    
    # EMPLOYEES
    @staticmethod
    def employee_matricule(matricule):
        return generate_cache_key("hr:employees:matricule", matricule)
    
    @staticmethod
    def active_employees(department_id=None):
        return generate_cache_key("hr:employees:active", department_id or "all")
    
    @staticmethod
    def employee_family(employee_id):
        return generate_cache_key("hr:employees:family", employee_id)
    
    # JOBS
    @staticmethod
    def department_tree():
        return "hr:jobs:department_tree"
    
    @staticmethod
    def positions_by_family(family_id):
        return generate_cache_key("hr:jobs:positions", family_id)
    
    @staticmethod
    def current_position(employee_id):
        return generate_cache_key("hr:jobs:position", employee_id)
    
    # CALENDAR
    @staticmethod
    def holidays(start_date, end_date):
        return generate_cache_key("hr:calendar:holidays", start_date, end_date)
    
    @staticmethod
    def working_days(start_date, end_date):
        return generate_cache_key("hr:calendar:working_days", start_date, end_date)
    
    # BANKING
    @staticmethod
    def active_bank_accounts():
        return "hr:banking:active_accounts"
    
    @staticmethod
    def bank_account_by_iban(iban):
        return generate_cache_key("hr:banking:iban", iban)
    
    # RECRUITMENT
    @staticmethod
    def active_job_offers(department_id=None):
        return generate_cache_key("hr:recruitment:offers", department_id or "all")
    
    @staticmethod
    def qualified_candidates(job_offer_id):
        return generate_cache_key("hr:recruitment:qualified", job_offer_id)

