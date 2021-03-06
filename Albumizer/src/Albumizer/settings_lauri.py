﻿# This Python file uses the following encoding: utf-8
DEBUG=False
DATABASES = {
    'default': {
      'ENGINE': "django.db.backends.sqlite3", # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
      'NAME': "albumizer_lauri.db",
      'USER': "", # Not used with sqlite3.
      'PASSWORD': "", # Not used with sqlite3.
      'HOST': "", # Set to empty string for localhost. Not used with sqlite3.
      'PORT': "", # Set to empty string for default. Not used with sqlite3.
      }
    }
MEDIA_ROOT="d:/Koulu/PhotoAlbumUploads/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s M%(module)s P%(process)d T%(thread)d -- %(message)s"
        },
    },
    "handlers": {
        "common_log_file": {
            "filename": "m:/koulu/AlbumizerLogs/commonlog.txt",
            "class": "logging.FileHandler",
            "formatter": "verbose",
        },
        "payments_log_file": {
            "filename": "m:/koulu/AlbumizerLogs/paymentslog.txt",
            "class": "logging.FileHandler",
            "formatter": "verbose",
        },
        "userActions_log_file": {
            "filename": "m:/koulu/AlbumizerLogs/useractionlog.txt",
            "class": "logging.FileHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["common_log_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends": {
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "level": "DEBUG",
            "propagate": True,
        },
        "albumizer": {
            "handlers": ["common_log_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "albumizer.userActions": {
            "handlers": ["userActions_log_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "albumizer.payments": {
            "handlers": ["payments_log_file"],
            "level": "INFO",
            "propagate": False,
        },
    }
}
