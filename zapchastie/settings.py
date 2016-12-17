#  -*- coding: utf-8 -*-
"""
Django settings for zapchastie project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from oscar.defaults import *
from oscar import OSCAR_MAIN_TEMPLATE_DIR
from oscar import get_core_apps
import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import settings_local


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_l+4+_0xt9j=8*xj%dml+i8rsoa73#e%09fw^m7+yr611b15y&pa'

# SECURITY WARNING: don't run wiKEY_PREFIXth debug turned on in production!
DEBUG = settings_local.DEBUG
THUMBNAIL_DEBUG = settings_local.THUMBNAIL_DEBUG
ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS
DEBUG_TOOLBAR_CONFIG = settings_local.DEBUG_TOOLBAR_CONFIG

SITE_ID = 1
SHOP_NAME = 'zapchastie.com.ua'
# Application definition

INSTALLED_APPS = \
    [
        'flat',
        'dal',
        'dal_select2',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.flatpages',
        'django.contrib.redirects',
        'django.contrib.admin',
        'django.contrib.sitemaps',
        'debug_toolbar',
        'apps.seo',
        'djmoney_rates',
        'djng',
        'easy_thumbnails',
        'filer',
        'mptt',
        'apps.ex_sites',
        'apps.ex_flatpages',
        'ckeditor',
        'import_export',
        'compressor',
        'widget_tweaks',
    ] + get_core_apps(
        [
            'apps.catalogue', 'apps.promotions', 'apps.partner', 'apps.dashboard', 'apps.dashboard.promotions',
            'apps.catalogue.reviews', 'apps.basket', 'apps.customer',
        ]
    )


MIDDLEWARE_CLASSES = settings_local.MIDDLEWARE_CLASSES

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'zapchastie.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'OPTIONS': {
            'loaders': [
                # ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
                # ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
                'django.core.context_processors.static',

                'oscar.apps.search.context_processors.search_form',
                'apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                'apps.seo.context_processors.meta_tags',
                'zapchastie.core.context_processors.metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'zapchastie.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': settings_local.DB_BACKEND,
        'NAME': settings_local.DB_NAME,
        'USER': settings_local.DB_USER,
        'PASSWORD': settings_local.DB_PASSWORD,
        'HOST': settings_local.DB_HOST,
        'POST': settings_local.DB_PORT,
        'ATOMIC_REQUESTS': settings_local.DB_ATOMIC_REQUESTS,
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('ru', _('Russia')),
)


import os
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', x)
from oscar import OSCAR_MAIN_TEMPLATE_DIR
TEMPLATE_DIRS = (
    location('templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
)

STATIC_URL = '/static_root/'
STATIC_ROOT = os.path.join(BASE_DIR,  'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR,  'media')
MEDIA_URL = "/media/"

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = 'images/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 650,
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}


CACHES = settings_local.CACHES
CACHE_MIDDLEWARE_SECONDS = settings_local.CACHE_MIDDLEWARE_SECONDS
KEY_PREFIX = settings_local.KEY_PREFIX

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

IMAGE_NOT_FOUND = 'image_not_found.jpg'
ADMINS = (('igor', 'shevchenkcoigor@gmail.com'),)
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings_local.EMAIL_HOST
EMAIL_PORT = settings_local.EMAIL_PORT
EMAIL_USE_TLS = settings_local.EMAIL_USE_TLS

OSCAR_DEFAULT_CURRENCY = 'USD'

THUMBNAIL_HIGH_RESOLUTION = True
FILER_CANONICAL_URL = 'sharing/'
FILER_DEBUG = DEBUG
FILER_ENABLE_LOGGING = DEBUG

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
    'easy_thumbnails.processors.background',
)

THUMBNAIL_DUMMY = True
THUMBNAIL_FORCE_OVERWRITE = True

WATERMARK = {
    'image': os.path.join(STATIC_ROOT, 'oscar/img/ui/dashboard/logo_oscar.png'),
    'transparency': 0.51
}

THUMBNAIL_ALIASES = {
    '': {
        'category_icon': {'size': (50, 30), 'crop': True},
        'basket_quick': {'size': (85, 50), 'crop': True},
        'basket_quick_product_image': {'size': (30, 30), 'crop': True},
        'basket_content': {'size': (150, 150), 'crop': True},
        'checkout': {'size': (150, 150), 'crop': True},
        'home_thumb_slide': {'size': (1170, 392), 'crop': True},
        'product_main': {'size': (556, 275), 'crop': True},
    },
}

# OPENEXCHANGE
# login -evgenij.bodnya@gmail.com
# pass - nNEeR?XCmH$UIkNwQFq}

DJANGO_MONEY_RATES = {
    'DEFAULT_BACKEND': 'djmoney_rates.backends.OpenExchangeBackend',
    'OPENEXCHANGE_URL': 'http://openexchangerates.org/api/latest.json',
    'OPENEXCHANGE_APP_ID': 'a4157eac5336497e963212eeee2e1b14',
    'OPENEXCHANGE_BASE_CURRENCY': 'USD',
}
OSCAR_CURRENCY_FORMAT = u'грн.'
BASE_CURRENCY = 'UAH'

HTML_MINIFY = not DEBUG
KEEP_COMMENTS_ON_MINIFYING = False
EXCLUDE_FROM_MINIFYING = ('^admin/', )
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# X_FRAME_OPTIONS = 'DENY'
USE_ETAGS = not DEBUG

IMPORT_EXPORT_USE_TRANSACTIONS = True

FIXTURE_DIRS = (os.path.join(BASE_DIR, 'data/fixtures'), )
OSCAR_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
