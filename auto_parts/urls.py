"""auto_parts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from auto_parts.app import application
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
import settings
from django.contrib.sitemaps.views import sitemap
from apps.sitemap import ProductSitemap, CategorySitemap
from django.contrib.flatpages.sitemaps import FlatPageSitemap

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'flatpages': FlatPageSitemap,
}


urlpatterns = [
                  url(r'^admin/', admin.site.urls),
                  url(r'', include(application.urls)),
                  url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
