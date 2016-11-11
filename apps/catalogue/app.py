from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from apps.catalogue.views import ReviewsView
from django.conf.urls import include, url
from oscar.apps.catalogue.reviews.app import application as reviews_app
from oscar.core.application import Application


class ReviewsApplication(Application):
    name = None
    reviews_app = reviews_app

    def get_urls(self):
        urlpatterns = super(ReviewsApplication, self).get_urls()
        urlpatterns += [
            url(r'^(?P<product_slug>[\w-]*)/reviews/', include(self.reviews_app.urls)),
        ]
        return self.post_process_urls(urlpatterns)


class CatalogueApplication(CoreCatalogueApplication, ReviewsApplication):
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
