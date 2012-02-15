# This Python file uses the following encoding: utf-8
# Django settings for Albumizer project.

import os


DEBUG = True
TEMPLATE_DEBUG = True


PRICE_PER_ALBUM = 5
PRICE_PER_ALBUM_PAGE = 0.50
SHIPPING_EXPENSES = 8


SIMPLE_PAYMENT_SERVICE_URL = "http://webcourse.cs.hut.fi/payment/pay/"
SIMPLE_PAYMENT_SERVICE_SELLER_ID = "wsdTLAs2012"
SIMPLE_PAYMENT_SERVICE_SECRET = "a76562ae5654109c5c349d45a6e24d16"

TWITTER_HASHTAG = "Albumizer"
TWITTER_ACCOUNT = "aaltowsd2012s"


AUTHENTICATION_BACKENDS = (
    #basic username-password authentication backend
    'django.contrib.auth.backends.ModelBackend',
    #facebook authentication backend
    'albumizer.facebook_backend.FacebookBackend',
)

AUTH_PROFILE_MODULE = "albumizer.UserProfile"



# for the Django debug toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False
}



ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Aleksi Lukkarinen', 'aleksi.lukkarinen@aalto.fi'),
    ('Tomas Heiskanen', 'tomas.heiskanen@gmail.com'),
    ('Lauri Helkkula', 'lauri.helkkula@aalto.fi'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add '', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': "group024", # Or path to database file if using sqlite3.
        'USER': 'group024', # Not used with sqlite3.
        'PASSWORD': 'aApeLxAr', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    # "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "Albumizer.albumizer.context_processors.common_variables",
    'Albumizer.albumizer.context_processors.facebook_app_id',
)


# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/group024/public_html/uploads/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'uploads'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/home/group024/public_html/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j&k*i9%4#efkue=ze&5&4%@*p6j6k$-6bw7$8p=6f865f0=*w9'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'albumizer/templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'albumizer',
    'south',
    'debug_toolbar',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}



workstation_owner = os.environ["USER"].lower()
if workstation_owner == 'aleksi':
    from settings_aleksi import *
elif workstation_owner == 'tomas':
    from settings_tomas import *
elif workstation_owner == 'lauri':
    from settings_lauri import *

from settings_facebook import *

