from .apps import INSTALLED_APPS


ACCESS_MANAGER_SCOPE = "access"
ACCESS_MANAGER_GROUP = "manager"  # Must match a slug in PERMISSION_PRESET["group"]
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
            "name": "Manager RH", 
            "slug": "hr_manager"
        },
        {
            "name": "Employé", 
            "slug": "employee"
        },
    ],
    "group": [
        {
            "name": "Gestion Administrative",
            "slug": "manager", 
            "roles": ["admin"]
        },
        {
            "name": "Administrateurs",
            "slug": "admins",
            "roles": ["admin"]
        },
        {
            "name": "Direction RH",
            "slug": "hr_dir",
            "roles": ["hr_manager"]
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

        # --- ROLE: HR MANAGER ---
        # Full operational management + Read access to access
        {
            "role": "hr_manager", 
            "scope": "access", 
            "actions": ["r"]
        },
        {
            "role": "hr_manager", 
            "scope": "employees", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr_manager", 
            "scope": "leaves", 
            "actions": ["r", "w", "u", "d", "a"] # 'a' for approval
        },
        {
            "role": "hr_manager", 
            "scope": "attendance", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr_manager", 
            "scope": "recruitment", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr_manager", 
            "scope": "jobs", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr_manager", 
            "scope": "calendar", 
            "actions": ["r", "w", "u", "d"]
        },
        {
            "role": "hr_manager", 
            "scope": "payroll", 
            "actions": ["r", "a"] # Final consultation and validation
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
    ]
}

