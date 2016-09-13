#  -*- coding: utf-8 -*-
"""
Django settings for auto_parts project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from oscar.defaults import *
from oscar import OSCAR_MAIN_TEMPLATE_DIR
from oscar import get_core_apps
import settings_local
import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_l+4+_0xt9j=8*xj%dml+i8rsoa73#e%09fw^m7+yr611b15y&pa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings_local.DEBUG
THUMBNAIL_DEBUG = settings_local.THUMBNAIL_DEBUG
ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS
DEBUG_TOOLBAR_CONFIG = settings_local.DEBUG_TOOLBAR_CONFIG

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'flat',
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'compressor',
    'widget_tweaks',
    'import_export',
    'debug_toolbar',
] + get_core_apps(['apps.catalogue'])

MIDDLEWARE_CLASSES = settings_local.MIDDLEWARE_CLASSES

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'auto_parts.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                'auto_parts.core.context_processors.metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'auto_parts.wsgi.application'


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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('ru', _('Russia')),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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

OSCAR_DEFAULT_CURRENCY = 'UAH'
OSCAR_CURRENCY_FORMAT = u'#,##0.## грн.'
