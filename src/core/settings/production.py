from .base import *

# SECURITY WARNING
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING
DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

# Remove debug toolbar in prod
# if "debug_toolbar" in INSTALLED_APPS:
#     INSTALLED_APPS.remove("debug_toolbar")

# Cache configuration for production
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_CACHE_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "bookstore",
    }
}

AXES_CACHE = "default"

# Axes for production
AXES_FAILURE_LIMIT = 5
AXES_RESET_ON_SUCCESS = True
AXES_COOLOFF_TIME = 1  # 1 hour
AXES_LOCKOUT_TEMPLATE = "authentication/lockout.html"
AXES_ENABLE_ADMIN = True

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
