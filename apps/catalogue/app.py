from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.conf.urls import url
from apps.catalogue.views import ReviewsView


class CatalogueApplication(CoreCatalogueApplication):
    def get_urls(self):
        urlpatterns = [
            url(r'comments/$', ReviewsView.as_view(), name='list-reviews'),
            url(r'^category/(?P<category_slug>[\w-]+(/(?!filter)[\w-]+(?!filter))*)(?:/filter/(?P<filter_slug>[\w-]+(/[\w-]+)*))*/$',
                self.category_view.as_view(), name='category'),
            url(r'^(?P<product_slug>[\w-]*)/$', self.detail_view.as_view(), name='detail'),
        ]
        urlpatterns += super(CatalogueApplication, self).get_urls()
        return urlpatterns

application = CatalogueApplication()
