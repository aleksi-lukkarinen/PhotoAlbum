# This Python file uses the following encoding: utf-8

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