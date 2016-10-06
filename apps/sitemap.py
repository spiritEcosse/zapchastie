from django.contrib.sitemaps import Sitemap
from apps.catalogue.models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return Product.objects.filter(enable=True)

    def lastmod(self, obj):
        return obj.date_updated


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Category.objects.filter(enable=True)

    def lastmod(self, obj):
        return obj.created

