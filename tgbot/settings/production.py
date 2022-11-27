import os
from .base import *
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', '0rk8u5wk=gav4dn@mw^p@c22-j^_gcg6s@-=jwxeo6j94@)pyh')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = os.path.exists('db.sqlite3')

ALLOWED_HOSTS = ['mi-asistente-herbalife.herokuapp.com']

POSTGRES_DB         = config('POSTGRES_DB', default=None)
POSTGRES_PASSWORD   = config('POSTGRES_PASSWORD', default=None)
POSTGRES_USER       = config('POSTGRES_USER', default=None)
POSTGRES_HOST       = config('POSTGRES_HOST', default=None)
POSTGRES_PORT       = config('POSTGRES_PORT', default=0, cast=int)

POSTGRES_READY = (
    POSTGRES_DB is not None
    and POSTGRES_PASSWORD is not None
    and POSTGRES_USER is not None
    and POSTGRES_HOST is not None
    and POSTGRES_PORT is not None
)

try:
    if POSTGRES_READY:
        DATABASES = {
            'default' : {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': POSTGRES_DB,
                'USER': POSTGRES_USER,
                'PASSWORD': POSTGRES_PASSWORD,
                'HOST': POSTGRES_HOST,
                'PORT': POSTGRES_PORT
            }
    }
except:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL')
        )
    }

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


