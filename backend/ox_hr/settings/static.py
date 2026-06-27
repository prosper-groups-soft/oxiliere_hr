from .base import BASE_DIR, DEBUG


STATIC_URL = 'static/'

if not DEBUG:
    STATIC_ROOT = BASE_DIR.parent / 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR.parent / "media/"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

