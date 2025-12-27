"""
Database settings for core project.
"""
from .base import BASE_DIR


# --- TEST Configuration (SQLite3) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Old Configuration (PostgreSQL / Tenants) ---
# DATABASE_URL = os.environ.get("DATABASE_URL")

# DATABASES = {
#     "default": dj_database_url.config(
#         default=DATABASE_URL,
#         engine='django_tenants.postgresql_backend'
#     )
# }

# DATABASE_ROUTERS = (
#     'django_tenants.routers.TenantSyncRouter',
# )

