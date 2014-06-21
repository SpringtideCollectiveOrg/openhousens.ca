"""
Django settings for openhousens project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# @see https://devcenter.heroku.com/articles/getting-started-with-django#settings-py

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://localhost/openhousens')}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'oy8$$i(*9eq73=8)1vq&v+xqpzig0%+b9wb*chpnol@k+pf)tv')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not os.getenv('PRODUCTION', False)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # @see http://mysociety.github.io/sayit/install/#installing-sayit-as-a-django-app
    'django.contrib.humanize',
    'haystack',
    'south',
    'tastypie',
    'pagination',
    'pipeline',
    'django_select2',
    'django_bleach',
    'popolo',
    'popit',
    'instances',
    'speeches',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # @see http://mysociety.github.io/sayit/install/#installing-sayit-as-a-django-app
    'speeches.middleware.InstanceMiddleware',
)

ROOT_URLCONF = 'openhousens.urls'

WSGI_APPLICATION = 'openhousens.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


# @see http://mysociety.github.io/sayit/install/#installing-sayit-as-a-django-app
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': os.getenv('ELASTICSEARCH_URL', 'http://127.0.0.1:9200/'),
        'INDEX_NAME': 'openhousens',
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None
PIPELINE_COMPILERS = (
    'pipeline_compass.compass.CompassCompiler',
)
PIPELINE_COMPASS_ARGUMENTS = '-r zurb-foundation'
PIPELINE_CSS = {
    'sayit-default': {
        'source_filenames': (
            'speeches/sass/speeches.scss',
        ),
        'output_filename': 'css/speeches.css',
    },
}
PIPELINE_JS = {
    'sayit-default-head': {
        'source_filenames': (
            'speeches/js/jquery.js',
        ),
        'output_filename': 'js/sayit.head.min.js',
    },
    'sayit-default': {
        'source_filenames': (
            'speeches/js/foundation/foundation.js',
            'speeches/js/foundation/foundation.dropdown.js',
            'speeches/js/speeches.js',
        ),
        'output_filename': 'js/sayit.min.js',
    },
    'sayit-player': {
        'source_filenames': (
            'speeches/mediaelement/mediaelement-and-player.js',
        ),
        'output_filename': 'js/sayit.mediaplayer.min.js',
    },
    'sayit-upload': {
        'source_filenames': (
            'speeches/js/jQuery-File-Upload/js/vendor/jquery.ui.widget.js',
            'speeches/js/jQuery-File-Upload/js/jquery.iframe-transport.js',
            'speeches/js/jQuery-File-Upload/js/jquery.fileupload.js',
        ),
        'output_filename': 'js/sayit.upload.min.js',
    },
}

BLEACH_ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'i', 'u', 'span', 'sub', 'sup', 'br',
    'p',
    'ol', 'ul', 'li',
    'table', 'caption', 'tr', 'th', 'td',
]
BLEACH_ALLOWED_ATTRIBUTES = {
    '*': [ 'id', 'title' ], # class, style
    'a': [ 'href' ],
    'li': [ 'value' ],
}
