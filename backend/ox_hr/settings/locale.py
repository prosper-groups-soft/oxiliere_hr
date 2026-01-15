from .base import BASE_DIR



LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Africa/Lubumbashi'

USE_TZ = True

USE_I18N = True

USE_TZ = True

USE_L10N = True

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
