"""
Applications settings for core project.
"""


"""
    Tenant will be coded later
    SHARED_APPS = (
        'django_tenants',
        'ox_tenants',

        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.humanize',

        'corsheaders',
        'django_filters',
        'ninja',
        'ninja_extra',
        'ninja_jwt',
        'utils_mixins',
    )

    TENANT_APPS = (
        'safedelete',
        'auditlog',
        'users',
        'hr'
    )
    
"""

INSTALLED_APPS = [
    #'django_tenants',
    #'ox_tenants',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'sequences',
    'corsheaders',
    'django_filters',
    'ninja',
    'ninja_extra',
    'ninja_jwt',
    'safedelete',
    'auditlog',
    'users',
    'hr',
    'utils_mixins',
]

MIDDLEWARE = [
    #'django_tenants.middleware.main.TenantMainMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ox_hr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ox_hr.wsgi.application'
ASGI_APPLICATION = 'ox_hr.asgi.application'

