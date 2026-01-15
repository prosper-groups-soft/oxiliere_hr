from .base import BASE_DIR


LOG_FILE_PATH = BASE_DIR.parent.parent / 'logs' / 'hr_logs.log'
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


HR_LOGGING_CONFIG = {
    'formatters': {
        'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'hr_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'formatter': 'standard',
            'maxBytes': 5242880,
            'backupCount': 5,
        },
    },
    'loggers': {
        'hr': {
            'handlers': ['hr_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
