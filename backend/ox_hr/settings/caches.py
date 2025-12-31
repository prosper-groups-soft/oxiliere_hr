import os

REDIS_URL = os.environ.get("REDIS_URL")

CACHEOPS_REDIS = REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

CACHEOPS_DEFAULTS = {
    'timeout': 60*60
}

CACHEOPS = {
    'core.*': {'ops': 'all', 'timeout': 60*15},
    'oxiliere.*': {'ops': 'all', 'timeout': 60*15},
    'permissions.*': {'ops': 'all', 'timeout': 60*15},
}
