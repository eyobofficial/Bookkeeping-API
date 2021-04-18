from .base import *


DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'dukka-api-dev.us-east-1.elasticbeanstalk.com'
]
ENVIRONMENT = 'development'


INSTALLED_APPS += [
    'django_extensions',
]
