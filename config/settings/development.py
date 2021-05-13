from .base import *


DEBUG = True
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
ENVIRONMENT = 'development'


INSTALLED_APPS += [
    'django_extensions',
]

# Static & media files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # AWS S3
    AWS_ACCESS_KEY_ID = config('S3_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = config('S3_SECRET_KEY')
    AWS_STORAGE_BUCKET_NAME = config('S3_BUCKET_NAME')
    AWS_S3_CUSTOM_DOMAIN = f'{ AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }


    # Static
    STATIC_LOCATION = 'staticfiles'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'config.storage_backends.S3StaticStorage'


    # Media
    MEDIA_LOCATION = 'mediafiles'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'config.storage_backends.S3MediaStorage'

else:
    # Static
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # Media
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
