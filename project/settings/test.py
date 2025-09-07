from .base import *  # noqa: F403
import environ

env = environ.Env()

# We want to set DEBUG to True but still maintain the ability to
# override it via env vars if needed.
DEBUG = env.bool("DJANGO_DEBUG", True)

# Use SQLite for testing for faster test execution
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-memory database for fastest tests
    }
}
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
