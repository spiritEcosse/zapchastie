from django.contrib.sites.shortcuts import get_current_site
from django.contrib.flatpages.models import FlatPage


def metadata(request):
    """
    Override metadata of oscar.
    """
    current_site = get_current_site(request)
    
    return {
        'shop_name': current_site.name,
        'shop_tagline': current_site.domain,
        'current_site': current_site
    }
