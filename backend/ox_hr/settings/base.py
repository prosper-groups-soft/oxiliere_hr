import os
from pathlib import Path
from oxutils.settings import oxi_settings
from oxutils.constants import ORGANIZATION_HEADER_KEY
from corsheaders.defaults import default_headers



ENV_PROD = "PROD"
ENV_DEV = "DEV"
ENV_STG = "STG"


BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get('DJANGO_DEBUG', 'OFF') == "ON"
ENVIRONNMENT = os.environ.get('DJANGO_ENVIRONNMENT', ENV_DEV)
APP_NAME = oxi_settings.service_name


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'secret_key') 


_ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*')
if _ALLOWED_HOSTS != '*':
    ALLOWED_HOSTS = _ALLOWED_HOSTS.split(',')
else:
    ALLOWED_HOSTS = [_ALLOWED_HOSTS]

_CSRF_TRUSTED_ORIGINS = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '*')
if _CSRF_TRUSTED_ORIGINS != '*':
    CSRF_TRUSTED_ORIGINS = _CSRF_TRUSTED_ORIGINS.split(',')
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]

_ALLOWED_ORIGINS = os.environ.get('DJANGO_ALLOWED_ORIGINS', '*')
if _ALLOWED_ORIGINS != '*':
    ALLOWED_ORIGINS = _ALLOWED_ORIGINS.split(',')
else:
    ALLOWED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'http://localhost:5173',
        'http://127.0.0.1:5173'
    ]



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

HOSTNAME_SPA = os.environ.get('HOSTNAME_SPA', "http://localhost:5173/")


CORS_ALLOWED_ORIGINS = ALLOWED_ORIGINS

# Définir le domaine parent commun pour les cookies
if ENVIRONNMENT == ENV_PROD:
    SESSION_COOKIE_DOMAIN = '.oxiliere.com'
    CSRF_COOKIE_DOMAIN = '.oxiliere.com'
else:
    SESSION_COOKIE_DOMAIN = 'localhost'
    CSRF_COOKIE_DOMAIN = 'localhost'

# Définir les cookies comme sécurisés si vous utilisez HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Définir les cookies comme SameSite=None pour permettre les requêtes cross-origin
SESSION_COOKIE_SAMESITE = 'None'  
CSRF_COOKIE_SAMESITE = 'None'



CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-session-token",
    "x-email-verification-key",
    "x-password-reset-key",
    ORGANIZATION_HEADER_KEY.lower(),
)
CORS_ALLOW_CREDENTIALS = True


NINJA_EXTRA={
    'PAGINATION_CLASS': 'ninja_extra.pagination.PageNumberPaginationExtra',
    'THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'email_add': '5/hour',
        'email_verification': '10/hour',
        'email_modification': '20/hour',
    }
}


SITE_NAME = os.environ.get('OXI_SITE_NAME', 'Oxiliere')
SITE_DOMAIN = os.environ.get('OXI_SITE_DOMAIN', 'oxiliere.com')

