﻿# This Python file uses the following encoding: utf-8

import os
#from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.views.generic.simple import redirect_to
import views




#
# For simple accounts without need for http-method-based dispatch
#
urlpatterns = patterns('albumizer.views',
    (r'^$', 'welcome_page'),

    (r'^album/$', 'list_all_visible_albums'),
    (r'^album/(?P<album_id>\d+)/$', 'show_single_album'),
    (r'^album/(?P<album_id>\d+)/s/(?P<secret_hash>[a-z0-9]{64})/$', 'show_single_album_with_hash'),
    (r'^album/(?P<album_id>\d+)/edit/$', 'edit_album'),
    (r'^album/(?P<album_id>\d+)/add_to_cart/$', 'add_album_to_shopping_cart'),
    (r'^album/(?P<album_id>\d{1,})/(?P<page_number>\d{1,})$', 'show_single_page'),

    (r'^accounts/$', redirect_to, {'url': "/accounts/profile/"}),
    (r'^accounts/logout/$', 'log_out'),
    (r'^accounts/profile/$', 'show_profile'),
    (r'^accounts/information/$', 'edit_account_information'),
    (r'^accounts/facebooklogin$', 'facebook_login'),

    (r'^order/$', redirect_to, {'url': '/order/information/'}),
    (r'^order/information/$', 'get_ordering_information'),
    (r'^order/summary/$', 'show_order_summary'),
    (r'^order/successful/$', 'report_order_as_successful'),

    (r'^"payment/sps/(?P<status>\w+)/$', 'report_sps_payment_status'),

    (r'^api/json/album/latest/$', redirect_to, {'url': '/api/json/album/latest/20/'}),
    (r'^api/json/album/latest/(?P<how_many>\d{1,2})/$', 'api_json_get_latest_albums'),
    (r'^api/json/album/random/$', redirect_to, {'url': '/api/json/album/random/4/'}),
    (r'^api/json/album/random/(?P<how_many>\d)/$', 'api_json_get_random_albums'),
    (r'^api/json/album/count/$', 'api_json_get_album_count'),
    (r'^api/json/user/count/$', 'api_json_get_user_count'),
)


#
# For views that require http-method-based dispatch
#
urlpatterns += patterns('',
    (r'^album/create/$', views.dispatch_by_method,
        {"GET": views.create_album_GET, "POST": views.create_album_POST}, "create_album"),
    (r'^accounts/login/$', views.dispatch_by_method, {"GET": views.log_in_GET, "POST": views.log_in_POST}, "log_in"),
    (r'^accounts/register/$', views.dispatch_by_method, {
        "GET": views.get_registration_information_GET, "POST": views.get_registration_information_POST},
        "get_registration_information"),
    (r'^cart/$', views.dispatch_by_method, {
        "GET": views.edit_shopping_cart_GET, "POST": views.edit_shopping_cart_POST},
        "edit_shopping_cart"),
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
