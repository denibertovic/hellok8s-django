from .base import *  # noqa: F403
import environ

env = environ.Env()

# Production-specific settings
DEBUG = env.bool("DJANGO_DEBUG", False)

# for static files
STORAGES = {
    "default": {
        "BACKEND": "core.customstorage.PublicMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "core.customstorage.StaticStorage",
    },
}

# Remove query string since the bucket is public
AWS_QUERYSTRING_AUTH = False

# This should make the static url be servable via nginx
AWS_S3_CUSTOM_DOMAIN = "hellok8s-django.deni.cloud"

# another option is to get secrets directly from a secret store like
# hashicorp vault (or similar) - either during bootup or on-demand
AWS_ACCESS_KEY_ID = env.get_value("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get_value("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = env.get_value("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env.get_value("AWS_S3_REGION_NAME")

AWS_DEFAULT_ACL = "public-read"
AWS_S3_SIGNATURE_VERSION = "s3v4"

AWS_S3_HOST = "s3.%s.scw.cloud" % (AWS_S3_REGION_NAME,)
AWS_S3_ENDPOINT_URL = "https://%s" % (AWS_S3_HOST,)

# Celery production overrides
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
