from oscar import app
from apps.catalogue.admin import FeatureAutocomplete, CategoriesAutocomplete, ProductAutocomplete
from django.conf.urls import url, include


class AutoParts(app.Shop):
    def get_urls(self):
        urlpatterns = [
            url(r'^admin/feature-autocomplete/$', FeatureAutocomplete.as_view(), name='feature-autocomplete'),
            url(r'^admin/product-autocomplete/$', ProductAutocomplete.as_view(), name='product-autocomplete'),
            url(r'^admin/categories-autocomplete/$', CategoriesAutocomplete.as_view(), name='categories-autocomplete'),
            url(r'^ckeditor/', include('ckeditor_uploader.urls')),
            url(r'^filer/', include('filer.urls')),
        ]
        urlpatterns += super(AutoParts, self).get_urls()
        return urlpatterns

application = AutoParts()
