from oscar import app
from apps.catalogue.admin import FeatureAutocomplete
from django.conf.urls import url


class AutoParts(app.Shop):
    def get_urls(self):
        urlpatterns = [
            url(r'^admin/feature-autocomplete/$', FeatureAutocomplete.as_view(), name='feature-autocomplete'),
        ]
        urlpatterns += super(AutoParts, self).get_urls()
        return urlpatterns

application = AutoParts()
