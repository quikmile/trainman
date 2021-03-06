"""
Django settings for trainman project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dnz_az7^5(m*0)wo^9pb-&!3&#e%e4p%@!+#46hrlw@=hvn)n^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

ADMINS = [('Abhishek Verma', 'abhishek@artificilabs.com')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_slack',
    'apps.xauth',
    'apps.servers',
    'apps.databases',
    'apps.services',
]

MIDDLEWARE = [
    # 'apps.custom.middleware.global_request.CurrentRequest',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trainman.urls'

TEMPLATE_DIR = os.path.join(os.getcwd(), "templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'trainman.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'trainman'),
        'USER': os.environ.get('DB_USER', 'trainman'),
        'PASSWORD': os.environ.get('DB_PASS', 'trainman'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

APPEND_SLASH = True

LOGIN_URL = '/login/'

XDATE_FORMAT = '%H:%M %b %d, %Y'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STATIC_ROOT = os.path.join(os.getcwd(), "staticfiles")

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'xauth.XUser'

GITLAB_ACCESS_TOKEN = 'Ry69Hmm2k6kwYjHaza6L'
GITLAB_API = 'https://gitlab.com/api/v4/'
GITLAB_USERNAME = os.environ.get('GITLAB_USERNAME', 'technomaniac')
GITLAB_PASSWORD = os.environ.get('GITLAB_PASSWORD', '08101en038')

ANSIBLE_DIR = os.path.join(BASE_DIR, "ansible/")
ANSIBLE_PLAYBOOK = os.path.join(ANSIBLE_DIR, "playbook.yml")
ANSIBLE_SSH_USER = os.environ.get('ANSIBLE_SSH_USER', 'artifici')
ANSIBLE_SSH_PASS = os.environ.get('ANSIBLE_SSH_PASS', 'artifici')
ANSIBLE_PUBLIC_KEY = os.environ.get('ANSIBLE_PUBLIC_KEY', '/home/artifici/.ssh/id_rsa')

BROKER_URL = os.environ.get('BROKER_URL', 'amqp://')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'amqp://')
CELERY_REDIRECT_STDOUTS_LEVEL = 'INFO'

ANSIBLE_CONFIG = os.path.join(ANSIBLE_DIR, "ansible.cfg")

os.environ.setdefault('ANSIBLE_CONFIG', ANSIBLE_CONFIG)

SLACK_TOKEN = 'xoxp-133294310241-134061212741-150399949303-995e018f74eef9a5d858c29fafce6819'
SLACK_BACKEND = 'django_slack.backends.CeleryBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'slack_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'slack-error': {
            'level': 'ERROR',
            'api_key': SLACK_TOKEN,
            'class': 'slacker_log_handler.SlackerLogHandler',
            'channel': '#infra'
        },
        'slack-info': {
            'level': 'INFO',
            'api_key': SLACK_TOKEN,
            'class': 'slacker_log_handler.SlackerLogHandler',
            'channel': '#infra'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'slack-error'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO')
        }
    }
}
