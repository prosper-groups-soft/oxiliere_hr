"""
Provides tools for inspecting and managing cache in development and production.
Get comprehensive cache statistics from Redis.
"""

from django.core.cache import cache
from django.http import JsonResponse
from django.contrib.auth.decorators import (
    login_required, permission_required
)
from django_redis import get_redis_connection


def get_cache_stats():
    """
    Cache debugging and monitoring utilities.

    Returns:
        Dict with cache stats
    """
    try:
        
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        total_keys = redis_conn.dbsize()
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total_requests = hits + misses
        
        return {
            'status': 'connected',
            'total_keys': total_keys,
            'memory_bytes': info.get('used_memory', 0),
            'memory_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
            'memory_human': info.get('used_memory_human', 'N/A'),
            'hits': hits,
            'misses': misses,
            'hit_rate': round((hits / total_requests * 100), 2) if total_requests > 0 else 0,
            'evictions': info.get('evicted_keys', 0),
            'connected_clients': info.get('connected_clients', 0),
            'uptime_seconds': info.get('uptime_in_seconds', 0),
            'version': info.get('redis_version', 'N/A'),
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


def get_cache_keys_by_pattern(pattern):
    """
    Get all cache keys matching a pattern.
    
    WARNING: This operation is slow on large Redis instances.
    Only use for debugging.
    
    Args:
        pattern: Pattern to match (with wildcards)
    
    Returns:
        List of matching keys
    """
    try:
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(f"*{pattern}*")
        
        return {
            'pattern': pattern,
            'count': len(keys),
            'keys': [k.decode() if isinstance(k, bytes) else k for k in keys[:100]]  # Limit to 100
        }
    except Exception as e:
        return {
            'error': str(e)
        }


def get_cache_key_size(cache_key):
    """
    Get size of a specific cache key.
    
    Args:
        cache_key: Key to check
    
    Returns:
        Size in bytes
    """
    try:
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        size = redis_conn.memory_usage(cache_key)
        
        return {
            'key': cache_key,
            'size_bytes': size,
            'size_kb': round(size / 1024, 2) if size else 0
        }
    except Exception as e:
        return {
            'error': str(e)
        }


def get_module_cache_usage(module_prefix):
    """
    Get cache usage for a specific module.
    
    Args:
        module_prefix: Module prefix (e.g., 'hr:payroll')
    
    Returns:
        Dict with module cache statistics
    """
    try:
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(f"*{module_prefix}*")
        
        total_size = 0
        for key in keys:
            size = redis_conn.memory_usage(key) or 0
            total_size += size
        
        return {
            'module': module_prefix,
            'key_count': len(keys),
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 2),
            'total_size_mb': round(total_size / 1024 / 1024, 2),
        }
    except Exception as e:
        return {
            'error': str(e)
        }


def get_all_modules_cache_usage():
    """
    Get cache usage for all HR modules.
    
    Returns:
        Dict with usage per module
    """
    modules = [
        'hr:payroll',
        'hr:leaves',
        'hr:attendance',
        'hr:employees',
        'hr:jobs',
        'hr:calendar',
        'hr:banking',
        'hr:recruitment',
    ]
    
    usage = {}
    for module in modules:
        usage[module] = get_module_cache_usage(module)
    
    return usage


def clear_cache_by_pattern(pattern):
    """
    Clear all cache keys matching a pattern.
    
    Args:
        pattern: Pattern to match
    
    Returns:
        Number of keys deleted
    """
    try:
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        keys = redis_conn.keys(f"*{pattern}*")
        
        if keys:
            deleted = redis_conn.delete(*keys)
            return {
                'pattern': pattern,
                'deleted': deleted,
                'success': True
            }
        else:
            return {
                'pattern': pattern,
                'deleted': 0,
                'success': True
            }
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }


def clear_module_cache(module_prefix):
    """
    Clear all cache for a specific module.
    
    Args:
        module_prefix: Module prefix (e.g., 'hr:payroll')
    
    Returns:
        Result dict
    """
    return clear_cache_by_pattern(module_prefix)


def clear_all_cache():
    """
    Clear all cache (use with extreme caution).
    
    Returns:
        Result dict
    """
    try:
        cache.clear()
        return {
            'success': True,
            'message': 'All cache cleared'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# =============================================
# Django Views for Cache Management
# =============================================

@login_required
@permission_required('auth.view_user', raise_exception=True)
def cache_stats_view(request):
    """API view to get cache statistics."""
    stats = get_cache_stats()
    return JsonResponse(stats)


@login_required
@permission_required('auth.view_user', raise_exception=True)
def cache_modules_usage_view(request):
    """API view to get cache usage per module."""
    usage = get_all_modules_cache_usage()
    return JsonResponse(usage, safe=False)


@login_required
@permission_required('auth.change_user', raise_exception=True)
def clear_module_cache_view(request, module_name):
    """API view to clear cache for a module."""
    result = clear_module_cache(f"hr:{module_name}")
    return JsonResponse(result)


@login_required
@permission_required('auth.change_user', raise_exception=True)
def clear_all_cache_view(request):
    """API view to clear all cache."""
    result = clear_all_cache()
    return JsonResponse(result)


# =============================================
# Management Command Helpers
# =============================================

def print_cache_stats():
    """Print cache statistics to console."""
    stats = get_cache_stats()
    
    print("\n" + "="*60)
    print("CACHE STATISTICS")
    print("="*60)
    
    if stats.get('status') == 'error':
        print(f"Error: {stats.get('error')}")
        return
    
    print(f"Status              : Connected")
    print(f"Total Keys          : {stats.get('total_keys', 0)}")
    print(f"Memory Used         : {stats.get('memory_human')} ({stats.get('memory_mb')} MB)")
    print(f"Cache Hits          : {stats.get('hits')}")
    print(f"Cache Misses        : {stats.get('misses')}")
    print(f"Hit Rate            : {stats.get('hit_rate')}%")
    print(f"Evictions           : {stats.get('evictions')}")
    print(f"Connected Clients   : {stats.get('connected_clients')}")
    print(f"Uptime              : {stats.get('uptime_seconds')} seconds")
    print(f"Redis Version       : {stats.get('version')}")
    print("="*60 + "\n")


def print_module_usage():
    """Print cache usage per module."""
    usage = get_all_modules_cache_usage()
    
    print("\n" + "="*60)
    print("CACHE USAGE BY MODULE")
    print("="*60)
    
    total_size_mb = 0
    
    for module, data in sorted(usage.items()):
        if 'error' not in data:
            size_mb = data.get('total_size_mb', 0)
            count = data.get('key_count', 0)
            total_size_mb += size_mb
            
            print(f"\n{module:25} | Keys: {count:5} | Size: {size_mb:8.2f} MB")
    
    print(f"\n{'TOTAL':25} | {'':20} | Size: {total_size_mb:8.2f} MB")
    print("="*60 + "\n")


# =============================================
# Healthcheck Helper
# =============================================

def check_cache_health():
    """
    Check cache health status.
    
    Returns:
        Dict with health status
    """
    stats = get_cache_stats()
    
    if stats.get('status') == 'error':
        return {
            'healthy': False,
            'error': stats.get('error')
        }
    
    # Analyze health
    total_keys = stats.get('total_keys', 0)
    memory_mb = stats.get('memory_mb', 0)
    hit_rate = stats.get('hit_rate', 0)
    
    health = {
        'healthy': True,
        'checks': {
            'connected': True,
            'memory_ok': memory_mb < 1000,  # Less than 1GB
            'hit_rate_good': hit_rate > 70,  # > 70%
            'key_count_ok': total_keys < 1000000,  # Less than 1M keys
        }
    }
    
    # Overall health
    health['healthy'] = all(health['checks'].values())
    health['warnings'] = []
    
    if memory_mb > 500:
        health['warnings'].append('Memory usage is high (> 500 MB)')
    
    if hit_rate < 50:
        health['warnings'].append('Hit rate is low (< 50%)')
    
    if total_keys > 500000:
        health['warnings'].append('Too many keys (> 500k)')
    
    if stats.get('evictions', 0) > 0:
        health['warnings'].append(f"Keys have been evicted ({stats.get('evictions')})")
    
    return health

