# This Python file uses the following encoding: utf-8

DEBUG = True



DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
#        "NAME": "d:/omat/Albumizer/albumizer_testdata.db",
#        "USER": "", # Not used with sqlite3.
#        "PASSWORD": "", # Not used with sqlite3.
#        "HOST": "", # Set to empty string for localhost. Not used with sqlite3.
#        "PORT": "", # Set to empty string for default. Not used with sqlite3.
#    }
    "default": {
        "ENGINE":   "postgresql_psycopg2", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME":     "Albumizer",
        "USER":     "albumizer", # Not used with sqlite3.
        "PASSWORD": "albumizer", # Not used with sqlite3.
        "HOST":     "localhost", # Set to empty string for localhost. Not used with sqlite3.
        "PORT":     "5432", # Set to empty string for default. Not used with sqlite3.
    }
}



LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "log_file": {
            "filename": "D:/Django-loki.txt",
            "encoding": "utf-8",
            "class": "logging.FileHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["log_file"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}


