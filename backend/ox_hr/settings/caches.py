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
    # Core
    'core.*': {'ops': 'all', 'timeout': 60*15},
    
    # PAYROLL - Very prioritary
    'hr.payroll.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h default
    },
    'payroll.payrollconfiguration': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h - stable config
    },
    'payroll.employeecontract': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60  # 1h
    },
    'payroll.payrollrun': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*15  # 15m
    },
    'payroll.salaryadvance': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m
    },
    'payroll.workeddaysrecord': {
        'ops': ('get', 'fetch'),
        'timeout': 60*30  # 30m
    },

    # LEAVES - Very prioritary
    'hr.leaves.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h default
    },
    'leaves.leavepolicy': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'leaves.seniorityrule': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'leaves.circumstanceleaverule': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'leaves.employeeleaveallocation': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60  # 1h
    },
    'leaves.leaverequest': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m
    },

    # ATTENDANCE
    'hr.attendance.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h default
    },
    'attendance.shiftpolicy': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'attendance.shiftdetail': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'attendance.punch': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*5  # 5m - real time
    },
    'attendance.dailyregister': {
        'ops': ('get', 'fetch'),
        'timeout': 60*10  # 10m
    },
    'attendance.timesheet': {
        'ops': ('get', 'fetch'),
        'timeout': 60*15  # 15m
    },

    # EMPLOYEES
    'hr.employees.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h
    },
    'employees.employee': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h - stable data
    },

    # JOBS
    'hr.jobs.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h
    },
    'jobs.jobfamily': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'jobs.position': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*24  # 24h
    },
    'jobs.department': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*24  # 24h
    },
    'jobs.employmentposition': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*12  # 12h
    },

    # CALENDAR - Very prioritary
    'hr.calendar.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h default
    },
    'calendar.calendarevent': {
        'ops': 'all',
        'timeout': 60*60*24*7  # 7 days
    },

    # BANKING
    'hr.banking.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h default
    },
    'banking.bank': {
        'ops': 'all',
        'timeout': 60*60*24*7  # 7 days
    },
    'banking.bankaccount': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60  # 1h
    },

    # RECRUITMENT
    'hr.recruitment.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m default
    },
    'recruitment.joboffer': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*24  # 24h
    },
    'recruitment.candidate': {
        'ops': ('get', 'fetch'),
        'timeout': 60*30  # 30m
    },
    'recruitment.application': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m
    },
    'recruitment.interview': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*15  # 15m
    },
    
    # Permissions & Auth
    'permissions.*': {'ops': 'all', 'timeout': 60*15},
}
