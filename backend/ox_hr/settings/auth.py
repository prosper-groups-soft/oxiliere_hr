import os
from datetime import timedelta





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

AUTHENTICATION_BACKENDS = []


AUTH_USER_MODEL = 'users.User'


# JWT Token
ACCESS_TOKEN_LIFETIME = timedelta(minutes=9),
REFRESH_TOKEN_LIFETIME = timedelta(days=7),
SIGNING_KEY = os.environ.get("SIGNING_KEY", "change_this_key")
