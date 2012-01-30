# This Python file uses the following encoding: utf-8

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
import albumizer.urls



admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include(albumizer.urls.urlpatterns)),

    url(r'^albumizer_manager/', include(admin.site.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^albumizer_manager/doc/', include('django.contrib.admindocs.urls')),
)
