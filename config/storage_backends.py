from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage


class S3StaticStorage(S3Boto3Storage):
    """
    S3 storage backend that saves the files locally, too.
    """
    location = 'staticfiles'
    default_acl = 'public-read'


class S3MediaStorage(S3Boto3Storage):
    location = 'mediafiles'
    default_acl = 'public-read'
    file_overwrite = False
