from django.conf.urls import include, url

from oscar.core.application import Application
from oscar.core.loading import get_class

from apps.catalogue.admin import FeatureAutocomplete, CategoriesAutocomplete, ProductAutocomplete


class Shop(Application):
    name = None

    catalogue_app = get_class('catalogue.app', 'application')
    promotions_app = get_class('promotions.app', 'application')
    search_app = get_class('search.app', 'application')
    offer_app = get_class('offer.app', 'application')

    def get_urls(self):
        urls = [
            url(r'^admin/feature-autocomplete/$', FeatureAutocomplete.as_view(), name='feature-autocomplete'),
            url(r'^admin/product-autocomplete/$', ProductAutocomplete.as_view(), name='product-autocomplete'),
            url(r'^admin/categories-autocomplete/$', CategoriesAutocomplete.as_view(), name='categories-autocomplete'),
            url(r'^ckeditor/', include('ckeditor_uploader.urls')),
            url(r'^filer/', include('filer.urls')),
            url(r'^catalogue/', include(self.catalogue_app.urls)),
            url(r'^search/', include(self.search_app.urls)),
            url(r'^offers/', include(self.offer_app.urls)),

            url(r'', include(self.promotions_app.urls)),
        ]
        return urls

application = Shop()
