"""
Database settings for core project.
"""

import os
import dj_database_url


DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        engine='django_tenants.postgresql_backend'
    )
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

