import os
from settings import BASE_DIR

DEFAULT_FROM_EMAIL = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEBUG = True
THUMBNAIL_DEBUG = DEBUG
AUTORELOAD = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        }
}

DEBUG_TOOLBAR_CONFIG = {
    'RENDER_PANELS': DEBUG,
}

CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = 'auto_part_'
KEY_PREFIX = CACHE_MIDDLEWARE_KEY_PREFIX

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
)

ALLOWED_HOSTS = ['*']

DB_BACKEND = 'django.db.backends.postgresql_psycopg2'
DB_NAME = os.path.basename(BASE_DIR)
DB_USER = 'postgres'
DB_PASSWORD = ''
DB_HOST = ''
DB_PORT = ''
DB_ATOMIC_REQUESTS = True
