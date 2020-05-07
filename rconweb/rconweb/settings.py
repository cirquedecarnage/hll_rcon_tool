"""
Django settings for rconweb project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os
import logging
from logging.config import dictConfig
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from rcon.extended_commands import Rcon
from rcon.settings import SERVER_INFO
import re
from sentry_sdk import configure_scope



try:
    ENVIRONMENT = re.sub('[^0-9a-zA-Z]+', '', (Rcon(SERVER_INFO).get_name() or "default").strip())[:64]
except:
    ENVIRONMENT = "undefined"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': f'[%(asctime)s][%(levelname)s][{ENVIRONMENT}] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
            },
        'file': {
            'level': 'DEBUG',
            'formatter': 'console',
            'class': 'logging.FileHandler',
            'filename':  os.getenv('DJANGO_LOGGING_PATH', f"{__package__}.log"),
            },
        },

    'loggers': {
        'rconweb': {
            'handlers': ['console', 'file'],
            'level': os.getenv('LOGGING_LEVEL', 'DEBUG'),
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        '__main__': {
            'handlers': ['console', 'file'],
            'level': os.getenv('LOGGING_LEVEL', 'DEBUG'),
            'propagate': True,
        }
    }
}


dictConfig(LOGGING)

sentry_logging = LoggingIntegration(
    level=logging.DEBUG,       # Capture debug and above as breadcrumbs
    event_level=logging.ERROR  # Send errors as events
)

# Switch to public integration if possible
sentry_sdk.init(
    dsn="https://78c97168e38343e9aba5435aebd94b2b@o60943.ingest.sentry.io/5220965",
    integrations=[DjangoIntegration(), sentry_logging],
    release=os.getenv("RELEASE_TAG", "dev"),
    environment=os.getenv('ENV', ENVIRONMENT),
    send_default_pii=True
)

with configure_scope() as scope:
    scope.set_extra("instance", ENVIRONMENT)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://78c97168e38343e9aba5435aebd94b2b@o60943.ingest.sentry.io/5220965",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# TODO: move that to env. We don't need it yet but we might
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9*i9zm1jx(5y-ns=*r6p%#6-q!bst98u3o3pw6joyf#-e(bh(0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", False)

ALLOWED_HOSTS = ['backend:8000', 'backend', '127.0.0.1', 'localhost']

# TODO: You might not want that. Think XSS
CORS_ORIGIN_ALLOW_ALL = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rconweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rconweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
