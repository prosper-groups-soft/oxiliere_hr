from .base import BASE_DIR



LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

USE_L10N = True


LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
]


LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
