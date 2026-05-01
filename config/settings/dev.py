from .base import *

SECRET_KEY = 'django-insecure-dev-only-do-not-use-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zaza_db',
        'USER': 'zaza_user',
        'PASSWORD': 'zaza_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}
