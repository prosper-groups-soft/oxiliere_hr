from celery.schedules import crontab
from .caches import REDIS_URL
from celery.schedules import crontab


# Celery Base Configuration
CELERY_TIMEZONE = "Africa/Lubumbashi"
CELERY_ENABLE_UTC = False
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes limit for a single tenant
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'


# Schedule
CELERY_BEAT_SCHEDULE = {
    'reset-annual-balances-every-january': {
        'task': 'hr.leaves.tasks.annual_leave_reset_orchestrator',
        'schedule': crontab(month_of_year=1, day_of_month=1, hour=0, minute=0),
    },
    'expire-carry-overs-daily': {
        'task': 'hr.leaves.tasks.expire_carry_overs_task',
        'schedule': crontab(hour=0, minute=5),  # 00:05 to avoid collision with resets
    },
    'mark-taken-daily': {
        'task': 'hr.leaves.tasks.mark_taken_daily_bulk',
        'schedule': crontab(hour=0, minute=10),  # 00:10 to allow for a buffer after expire_carry_overs
    },
    'backfill-rotation-shifts-daily': {
        'task': 'hr.attendance.tasks.orchestrate_rotation_backfill',
        'schedule': crontab(hour=1, minute=0),  # Runs daily at 01:00 AM
    },
}

