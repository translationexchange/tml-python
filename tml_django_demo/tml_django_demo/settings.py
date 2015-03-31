"""
Django settings for tml_django_demo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# add .. to pythonpath:
sys.path.append(os.path.dirname(BASE_DIR))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')s4^w=8dmt5#iigd@x!f#3=5qu8wp+5_suuc!^adz-@79cgofg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True
TEMPLATE_DIRS = (
    BASE_DIR + "/templates/",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django_tml',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django_tml.middleware.SetSourceToViewMiddleware',
    'django_tml.inline_translations.middleware.InlineTranslationsMiddleware'
)

ROOT_URLCONF = 'tml_django_demo.urls'

WSGI_APPLICATION = 'tml_django_demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR + '/tmp/',
    }
}

TML = {
    'token': '4cb7cf6bf7cd64120661ae7da67759076d9b08f233ae510012fc6c3e819b93b8',
    'monkeypatch': True,
    'cache': 'default',
    'inline_wrapper_cookie': 'tml_inline_translation'
}

TML_DATA_PREPROCESSORS = ['tml.tools.list.preprocess_lists',]