from .base import *


DEBUG = True
ALLOWED_HOSTS = [
    '.dukka-api-dev.us-east-1.elasticbeanstalk.com',
    '.localhost',
    '.127.0.0.1'
]
ENVIRONMENT = 'dev'

INSTALLED_APPS += [
    'django_extensions',
]
