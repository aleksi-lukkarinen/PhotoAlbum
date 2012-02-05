# This Python file uses the following encoding: utf-8

from django.contrib.sites.models import Site




def common_variables(request):
    current_site = Site.objects.get_current(
                                            )
    return {
        "site_domain": current_site.domain
    }
