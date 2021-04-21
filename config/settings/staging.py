from .base import *


DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ENVIRONMENT = 'staging'


# AWS S3
AWS_ACCESS_KEY_ID = config('S3_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = config('S3_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = config('S3_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}


# Static
STATIC_LOCATION = 'staticfiles'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
STATICFILES_STORAGE = 'config.storage_backends.S3StaticStorage'


# Media files
MEDIA_LOCATION = 'mediafiles'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'config.storage_backends.S3MediaStorage'
