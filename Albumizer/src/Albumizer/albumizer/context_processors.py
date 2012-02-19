# This Python file uses the following encoding: utf-8

from django.contrib.sites.models import Site
from django.conf import settings # import the settings file




def common_variables(request):
    current_site = Site.objects.get_current()

    return {
        "site_domain": current_site.domain,
        "site_name": current_site.name,
        "twitter_hashtag": settings.TWITTER_HASHTAG,
        "twitter_account": settings.TWITTER_ACCOUNT,
        "template_cache_timeout": 5 * 60
    }




def facebook_app_id(context):
    # return the value you want as a dictionary. you may add multiple values in there.
    return {'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID}
