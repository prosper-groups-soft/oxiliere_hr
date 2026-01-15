from datetime import timedelta
from oxutils.settings import oxi_settings


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


AUTH_USER_MODEL = 'users.User'


with open(oxi_settings.jwt_signing_key, 'rb') as f:
    SIGNING_KEY = f.read()

with open(oxi_settings.jwt_verifying_key, 'rb') as f:
    VERIFYING_KEY = f.read()


NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': "RS256",
    'SIGNING_KEY': SIGNING_KEY,
    'VERIFYING_KEY': VERIFYING_KEY,
    'UPDATE_LAST_LOGIN': True,
    'TOKEN_USER_CLASS': 'oxutils.jwt.models.TokenUser'
}

