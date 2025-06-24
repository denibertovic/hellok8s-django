from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage


class PublicMediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = "media"
    default_acl = "public-read"
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = "privatemedia"
    default_acl = "private"
    file_overwrite = True


class StaticStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = "static"
    default_acl = "public-read"
    file_overwrite = True
