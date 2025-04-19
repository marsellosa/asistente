
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    #
    'rest_framework',
    'django_htmx',
    #
    'bot',
    'comanda',
    'consumos',
    'finanzas',
    'home',
    'main',
    'operadores',
    'pedidos',
    'persona',
    'prepagos',
    'productos',
    'recetas',
    'reportes',
    'socios',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'tgbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tgbot.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'es-bo'

TIME_ZONE = 'America/La_Paz'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MEDIA_URL = 'AdminLTE/dist/img/'
# MEDIA_ROOT = BASE_DIR / "staticfiles" / "AdminLTE" / "dist" / "img"

STATICFILES_DIRS = [
    (BASE_DIR / "static"),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'

try:
    EMAIL_BACKEND       = config('EMAIL_BACKEND', default=None)
    EMAIL_HOST          = config('EMAIL_HOST', default=None)
    EMAIL_PORT          = config('EMAIL_PORT', default=0, cast=int)
    EMAIL_USE_TLS       = config('EMAIL_USE_TLS', default=False, cast=bool)
    EMAIL_HOST_USER     = config('EMAIL_HOST_USER', default=None)
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default=None)
    DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER
except:
    pass

EMAIL_READY = (
    EMAIL_BACKEND is not None and
    EMAIL_HOST is not None and
    EMAIL_PORT is not None and
    EMAIL_USE_TLS is not None and
    EMAIL_HOST_USER is not None and
    EMAIL_HOST_PASSWORD is not None
)
if EMAIL_READY:
    pass

# settings.py
TELEGRAM_BOT_TOKEN = config('TOKEN')  # Reemplaza con tu token real
