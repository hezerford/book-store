from .base import *

# SECURITY WARNING
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Debug Toolbar
# INSTALLED_APPS += ["debug_toolbar"]

# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# def show_toolbar(request):
#     return True

# DEBUG_TOOLBAR_CONFIG = {
#     "SHOW_TOOLBAR_CALLBACK": show_toolbar,
# }


INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Redis Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_CACHE_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}


AXES_CACHE = "default"

# Axes
AXES_FAILURE_LIMIT = 5
AXES_RESET_ON_SUCCESS = True
AXES_COOLOFF_TIME = 0.1
AXES_LOCKOUT_TEMPLATE = "authentication/lockout.html"
AXES_ENABLE_ADMIN = True
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Настройки для индексации
ELASTICSEARCH_DSL_AUTOSYNC = True
ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = (
    "django_elasticsearch_dsl.signals.RealTimeSignalProcessor"
)

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
