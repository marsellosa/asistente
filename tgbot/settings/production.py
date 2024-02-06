
from .base import *
from decouple import config

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['web-production-d293.up.railway.app', 'miasistenteherbalife.com']

PGDATABASE   = config('PGDATABASE', default=None)
PGPASSWORD   = config('PGPASSWORD', default=None)
PGUSER       = config('PGUSER', default=None)
PGHOST       = config('PGHOST', default=None)
PGPORT       = config('PGPORT', default=0, cast=int)

POSTGRES_READY = (
    PGDATABASE is not None
    and PGPASSWORD is not None
    and PGUSER is not None
    and PGHOST is not None
    and PGPORT is not None
)

try:
    if POSTGRES_READY:
        DATABASES = {
            'default' : {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': PGDATABASE,
                'USER': PGUSER,
                'PASSWORD': PGPASSWORD,
                'HOST': PGHOST,
                'PORT': PGPORT
            }
    }
except:
    pass

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


