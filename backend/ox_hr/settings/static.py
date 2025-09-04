from .base import BASE_DIR, DEBUG



STATIC_URL = 'static/'

if not DEBUG:
    STATIC_ROOT = BASE_DIR / 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / "media/"


COMPRESS_ROOT = BASE_DIR / 'static/'
COMPRESS_ENABLED = True

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
