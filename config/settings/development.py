from .base import *


DEBUG = True
ALLOWED_HOSTS = ['*']
ENVIRONMENT = 'dev'

INSTALLED_APPS += [
    'django_extensions',
]
