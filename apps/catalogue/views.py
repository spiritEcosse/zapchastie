from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView, \
    ProductDetailView as CoreProductDetailView
from django.utils.functional import cached_property
import logging
from apps.catalogue.models import Category, Feature, Product
from django.http import HttpResponsePermanentRedirect, Http404
from django.utils.http import urlquote
from oscar.core.loading import get_class
get_product_search_handler_class = get_class('catalogue.search_handlers', 'get_product_search_handler_class')

logger = logging.getLogger(__name__)


class ProductCategoryView(CoreProductCategoryView):
    feature_only = ('title', 'slug', 'parent__id', 'parent__title', )
    filter_slug = 'filter_slug'
    model_category = Category

    def get_category(self):
        category = super(ProductCategoryView, self).get_category()

        if not self.model_category.objects.filter(enable=True, pk=category.pk):
            raise Http404('"%s" does not exist' % self.request.get_full_path())
        return category

    def get(self, request, *args, **kwargs):
        self.kwargs['filter_slug_objects'] = self.selected_filters
        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    @cached_property
    def selected_filters(self):
        filter_slug = self.kwargs.get(self.filter_slug).split('/') if self.kwargs.get(self.filter_slug) else []
        features = Feature.objects.only(*self.feature_only).select_related('parent').filter(
            slug__in=filter_slug, level=1
        ).order_by('pk')

        if len(filter_slug) != features.count():
            raise Http404('"%s" does not exist' % self.request.get_full_path())

        return features

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            expected_path = category.get_absolute_url(self.kwargs)

            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_categories(self):
        """
        Return a list of the current category and its ancestors
        """
        return self.category.get_descendants(include_self=True)

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        context['url_extra_kwargs'] = {'category_slug': self.kwargs.get('category_slug')}
        context['selected_filters'] = self.selected_filters
        return context

    def get_search_handler(self, *args, **kwargs):
        kwargs['category'] = self.category
        kwargs['selected_filters'] = self.selected_filters
        return super(ProductCategoryView, self).get_search_handler(*args, **kwargs)


class ProductDetailView(CoreProductDetailView):
    def get_object(self, queryset=None):
        self.kwargs['slug'] = self.kwargs['product_slug']
        queryset = self.model.objects.filter(enable=True)
        return super(ProductDetailView, self).get_object(queryset=queryset)
