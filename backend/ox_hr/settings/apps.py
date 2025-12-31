from .base import BASE_DIR


SHARED_APPS = [
    'django_tenants',
    'cacheops',
    'core',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django_structlog',
    'corsheaders',
    'django_filters',
    'safedelete',
    'django_celery_results',
    'oxutils',
    'oxutils.users',
    'oxutils.currency',
    'oxutils.oxiliere',
    'ninja',
    'ninja_extra',
    'ninja_jwt',
]

TENANT_APPS = [
    'hr',
    'auditlog',
    'oxutils.audit',
    'oxutils.permissions',
    'sequences',
]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS

MIDDLEWARE = [
    'oxutils.oxiliere.middleware.TenantMainMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ninja.compatibility.files.fix_request_files_middleware',
]

ROOT_URLCONF = 'ox_hr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'oxutils.context.site_name_processor.site_name',
            ],
        },
    },
]

WSGI_APPLICATION = 'ox_hr.wsgi.application'
ASGI_APPLICATION = 'ox_hr.asgi.application'
