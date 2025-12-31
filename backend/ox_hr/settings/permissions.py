from .apps import INSTALLED_APPS

ACCESS_MANAGER_SCOPE = "access"      # Scope for access management endpoints
ACCESS_MANAGER_GROUP = "manager"     # Group filter (or None)
ACCESS_MANAGER_CONTEXT = {}          # Additional context dict

# List of valid scopes in your application
ACCESS_SCOPES = [
    "access",
]

# Enable permission check caching (requires cacheops)
CACHE_CHECK_PERMISSION = False

# if cacheops is installed, enable caching
if 'cacheops' in INSTALLED_APPS:
    CACHE_CHECK_PERMISSION = True


# settings.py
PERMISSION_PRESET = {
    "roles": [
        {"name": "Administrateur", "slug": "admin"},
    ],
    "group": [
        {
            "name": "Manager",
            "slug": "manager",
            "roles": ["admin"]
        },
    ],
    "role_grants": [
        {
            "role": "admin",
            "scope": "access",
            "actions": ["r", "w", "d", "u", "a"],
            "context": {}
            # No group = generic RoleGrant
        },
    ]
}
