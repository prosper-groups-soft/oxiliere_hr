import os
from .base import ENV_DEV, ENVIRONNMENT


EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'

# ONLY for development/testing use console
if ENVIRONNMENT == ENV_DEV:
    EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
    
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'ON') == "ON"
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
