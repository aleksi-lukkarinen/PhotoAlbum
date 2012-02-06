# This Python file uses the following encoding: utf-8

import os
import views
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to



#
# For simple accounts without need for http-method-based dispatch
#
urlpatterns = patterns('albumizer.views',
    (r'^$', 'welcome_page'),

    (r'^album/$', 'list_all_visible_albums'),
    (r'^album/(?P<album_id>\d{1,})/$', 'show_single_album'),
    (r'^album/(?P<album_id>\d{1,})/edit/$', 'edit_album'),
    (r'^album/(?P<album_id>\d{1,})/add_to_cart/$', 'add_album_to_shopping_cart'),

    (r'^accounts/$', redirect_to, {'url': '/accounts/profile/'}),
    (r'^accounts/logout/$', 'log_out'),
    (r'^accounts/profile/$', 'show_profile'),
    (r'^accounts/information/$', 'edit_account_information'),

    (r'^cart/$', 'edit_shopping_cart'),

    (r'^order/$', redirect_to, {'url': '/order/information/'}),
    (r'^order/information/$', 'get_ordering_information'),
    (r'^order/successful/$', 'report_order_as_succesful'),

    (r'^api/json/album/latest/$', redirect_to, {'url': '/api/json/album/latest/20/'}),
    (r'^api/json/album/latest/(?P<how_many>\d{1,2})/$', 'api_json_get_latest_albums'),
    (r'^api/json/album/random/$', redirect_to, {'url': '/api/json/album/random/4/'}),
    (r'^api/json/album/random/(?P<how_many>\d)/$', 'api_json_get_random_albums'),
)


#
# For views that require http-method-based dispatch
#
urlpatterns += patterns('',
    (r'^album/create/$', views.dispatch_by_method, {
        "GET": views.create_album_GET, "POST": views.create_album_POST
    }),
    (r'^accounts/login/$', views.dispatch_by_method, {
        "GET": views.log_in_GET, "POST": views.log_in_POST
    }),
    (r'^accounts/register/$', views.dispatch_by_method, {
        "GET": views.get_registration_information_GET,
        "POST": views.get_registration_information_POST
    }),
)


#
# COMMENT OUT IN PRODUCTION ENVIRONMENT!!
# For local development, when testing with DEBUG=False.
#
urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(os.path.dirname(__file__), 'static').replace('\\', '/'),
    }),
)
