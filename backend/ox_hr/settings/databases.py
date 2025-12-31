import os
import dj_database_url


DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        engine='django_tenants.postgresql_backend'
    )
}


TENANT_MODEL = 'core.Tenant'
TENANT_DOMAIN_MODEL = 'core.Domain'
TENANT_USER_MODEL = 'core.TenantUser'
