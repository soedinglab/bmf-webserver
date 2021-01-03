"""
Django settings for bmf_web project.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from os import path


class MissingConfigurationException(Exception):
    pass


def get_from_env(env_variable, converter=str, default=None):
    if env_variable not in os.environ:
        if default is None:
            raise MissingConfigurationException('Environment variable %s undefined' % env_variable)
        else:
            return default
    else:
        return converter(os.getenv(env_variable))

# CELERY SETTINGS
BROKER_URL = 'redis://redis_celery:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_from_env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_from_env('DJANGO_DEBUG', converter=lambda x: x == "1")


ALLOWED_HOSTS = get_from_env('ALLOWED_HOSTS', converter=lambda x: x.split())


# Application definition

INSTALLED_APPS = [
    'bmf',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'crispy_forms'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bmf_web.urls'

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

WSGI_APPLICATION = 'bmf_web.wsgi.application'

DB_HOST = get_from_env('DB_HOST')
DB_NAME = get_from_env('DB_NAME')
DB_USER = get_from_env('DB_USER')
DB_PORT = get_from_env('DB_PORT')
DB_PW = get_from_env('MYSQL_PASSWORD')

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PW,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

MEDIA_ROOT = '/media/'
MEDIA_URL = '/media/'

JOB_DIR_PREFIX = 'jobs'
JOB_DIR = path.join(MEDIA_ROOT, JOB_DIR_PREFIX)

LOG_DIR = '/logs'


# maximum upload file size in bytes. (20MiB)
MAX_UPLOAD_FILE_SIZE=20971520


# logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        },
    },
    'handlers': {
        'django_logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*100,
            'backupCount': 5,
            'filename': path.join(LOG_DIR, 'django.log'),
            'formatter': 'verbose'
        },
        'django_requests_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*100,
            'backupCount': 5,
            'filename': path.join(LOG_DIR, 'django_requests.log'),
            'formatter': 'verbose'
        },
        'bmf_logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*100,
            'backupCount': 5,
            'filename': path.join(LOG_DIR, 'bmf.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['django_requests_file'],
            'level': 'WARN',
            'propagate': True,
        },
        'bmf': {
            'handlers': ['bmf_logfile'],
            'level': get_from_env('BMF_LOG_LEVEL'),
            'propagate': True,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/static"


CRISPY_TEMPLATE_PACK = 'bootstrap4'
