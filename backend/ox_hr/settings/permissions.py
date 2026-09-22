from .apps import INSTALLED_APPS


ACCESS_MANAGER_SCOPE = "access"
ACCESS_MANAGER_ROLE = None     # No specific role required - any role with access permission works
ACCESS_MANAGER_GROUP = "system_admins"  # Must match a slug in PERMISSION_PRESET["group"]
ACCESS_MANAGER_CONTEXT = {}


ACCESS_SCOPES = [
    "access",
    "employees",
    "payroll",
    "leaves",
    "attendance",
    "recruitment",
    "jobs",
    "banking",
    "calendar",
    "performance",
]


CACHE_CHECK_PERMISSION = False
if 'cacheops' in INSTALLED_APPS:
    CACHE_CHECK_PERMISSION = True


# --- Permission Presets ---
PERMISSION_PRESET = {
    "roles": [
        {
            "name": "Administrateur Système", 
            "slug": "admin"
        },
        {
            "name": "Équipe RH", 
            "slug": "hr"
        },
        {
            "name": "Employé", 
            "slug": "employee"
        },
    ],
    "group": [
        {
            "name": "Administrateurs Système",
            "slug": "system_admins", 
            "roles": ["admin"]
        },
        {
            "name": "Direction Générale",
            "slug": "admins",
            "roles": ["admin"]
        },
        {
            "name": "Équipe RH",
            "slug": "hr_team",
            "roles": ["hr"]
        },
    ],
    "role_grants": [
        # --- ROLE: ADMIN ---
        # Full access to all specified scopes
        *[
            {
                "role": "admin",
                "scope": scope,
                "actions": ["r", "w", "d", "u", "a"],
            }
            for scope in ACCESS_SCOPES
        ],

        # --- ROLE: HR (Équipe RH) ---
        # Full operational management + Read/Write access to access
        {
            "role": "hr", 
            "scope": "access", 
            "actions": ["r", "w"]
        },
        {
            "role": "hr", 
            "scope": "employees", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr", 
            "scope": "leaves", 
            "actions": ["r", "w", "u", "d", "a"] # 'a' for approval
        },
        {
            "role": "hr", 
            "scope": "attendance", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr", 
            "scope": "recruitment", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr", 
            "scope": "jobs", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr", 
            "scope": "calendar", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr", 
            "scope": "payroll", 
            "actions": ["r", "a"] # Final consultation and validation
        },  
        {
            "role": "hr",
            "scope": "performance",
            "actions": ["r", "w", "u", "d"]
        },

        # --- ROLE: EMPLOYEE ---
        # Self-service strict with context of ownership ('own')
        {
            "role": "employee",
            "scope": "employees",
            "actions": ["r"],
            "context": {"own": True}
        },
        {
            "role": "employee",
            "scope": "leaves",
            "actions": ["r", "w"],
            "context": {"own": True}
        },
        {
            "role": "employee",
            "scope": "payroll",
            "actions": ["r"],
            "context": {"own": True}
        },
        {
            "role": "employee",
            "scope": "calendar",
            "actions": ["r"],
            "context": {"own": True}
        },
        {
            "role": "employee",
            "scope": "performance",
            "actions": ["r"],
            "context": {"own": True}
        },
    ]
}

