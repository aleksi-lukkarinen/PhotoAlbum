# This Python file uses the following encoding: utf-8

import os
from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to



urlpatterns = patterns('albumizer.views',
    (r'^$', 'welcome_page'),

    (r'^album/$', 'list_all_visible_albums'),
    (r'^album/create/$', 'create_albums'),
    (r'^album/(?P<album_id>\d{1,})/$', 'show_single_album'),
    (r'^album/(?P<album_id>\d{1,})/edit/$', 'edit_album'),

    (r'^accounts/$', redirect_to, {'url': '/accounts/profile/'}),
    (r'^accounts/login/$', 'log_in'),
    (r'^accounts/logout/$', 'log_out'),
    (r'^accounts/profile/$', 'show_profile'),
    (r'^accounts/information/$', 'edit_account_information'),
    (r'^accounts/register/$', 'get_registration_information'),

    (r'^cart/$', 'edit_shopping_cart'),

    (r'^order/$', redirect_to, {'url': '/order/information/'}),
    (r'^order/information/$', 'get_ordering_information'),
    (r'^order/successful/$', 'report_order_as_succesful'),
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
