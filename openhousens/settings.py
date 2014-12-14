"""
Django settings for openhousens project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'oy8$$i(*9eq73=8)1vq&v+xqpzig0%+b9wb*chpnol@k+pf)tv')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not os.getenv('PRODUCTION', False)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['openhousens.herokuapp.com', '.openhousens.ca']


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth', # needed by instances models
    'django.contrib.contenttypes', # needed by popolo models
    'django.contrib.staticfiles',
    # @see http://mysociety.github.io/sayit/install/#installing-sayit-as-a-django-app
    'haystack',
    'django_bleach',
    'easy_thumbnails',
    'popolo',
    'instances', # needed by speeches models
    'speeches',
    'legislature',
)

# @see https://docs.djangoproject.com/en/1.7/ref/middleware/#middleware-ordering
MIDDLEWARE_CLASSES = (
    # @see https://docs.djangoproject.com/en/1.7/ref/middleware/#django.middleware.gzip.GZipMiddleware
    'django.middleware.gzip.GZipMiddleware',
    # @see https://docs.djangoproject.com/en/1.7/topics/conditional-view-processing/
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'openhousens.urls'

WSGI_APPLICATION = 'openhousens.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'


# @see https://devcenter.heroku.com/articles/getting-started-with-django#settings-py
# @see https://devcenter.heroku.com/articles/django-assets

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://postgres@localhost/openhousens')}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static asset configuration
STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# @see http://mysociety.github.io/sayit/install/#installing-sayit-as-a-django-app
# @see http://django-haystack.readthedocs.org/en/latest/searchindex_api.html#keeping-the-index-fresh
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': os.getenv('ELASTICSEARCH_URL', 'http://127.0.0.1:9200/'),
        'INDEX_NAME': 'openhousens',
        'EXCLUDED_INDEXES': [
            'speeches.search_indexes.SpeechIndex',
            'speeches.search_indexes.SectionIndex',
        ],
    },
}
# @see http://django-haystack.readthedocs.org/en/latest/settings.html#haystack-custom-highlighter
HAYSTACK_CUSTOM_HIGHLIGHTER = 'legislature.highlighting.SafeHighlighter'

BLEACH_ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'i', 'u', 'span', 'sub', 'sup', 'br',
    'p', 'blockquote',
    'ol', 'ul', 'li',
    'table', 'caption', 'tr', 'th', 'td',
]
BLEACH_ALLOWED_ATTRIBUTES = {
    '*': [ 'id', 'title', 'class' ], # class, style
    'a': [ 'href' ],
    'li': [ 'value' ],
}

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',  # needed by pagination
)

# @see https://docs.djangoproject.com/en/1.7/topics/cache/#memcached
if os.getenv('PRODUCTION', False):
    from memcacheify import memcacheify
    CACHES = memcacheify()
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Error reporting.
ADMINS = (
    ('James McKinney', 'james@opennorth.ca'),
)
# @see https://sendgrid.com/docs/Integrate/Frameworks/django.html
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME', None)
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD', None)
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Error logging.
# @see https://github.com/etianen/django-herokuapp#outputting-logs-to-heroku-logplex
if os.getenv('PRODUCTION', False):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
            'speeches': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }
# SQL query logging.
elif os.getenv('VERBOSE', False):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'speeches': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }
