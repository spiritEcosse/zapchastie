from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import get_script_prefix
from django.utils.encoding import iri_to_uri


def get_absolute_url(self):
    return iri_to_uri(get_script_prefix() + self.url.strip(get_script_prefix()) + get_script_prefix())


FlatPage.get_absolute_url = get_absolute_url
