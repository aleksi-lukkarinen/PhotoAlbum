# This Python file uses the following encoding: utf-8

from django.conf.urls.defaults import handler404, handler500, include, patterns, url
from django.contrib import admin
import albumizer.urls




admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include(albumizer.urls.urlpatterns)),
    url(r'^albumizer_manager/doc/', include('django.contrib.admindocs.urls')),
    url(r'^albumizer_manager/', include(admin.site.urls)),
    )

from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
    url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, }),
    )


#
# For error pages
#
handler404 = "albumizer.views.display_HTTP404"
handler500 = "albumizer.views.display_HTTP500"
