from oscar.apps.catalogue.search_handlers import SimpleProductSearchHandler as CoreSimpleProductSearchHandler
from apps.catalogue.models import Product, Feature
from itertools import groupby
from django.db.models import Prefetch


class SimpleProductSearchHandler(CoreSimpleProductSearchHandler):
    feature_only = ('title', 'slug', 'parent__id', 'parent__title', )
    feature_orders = ('parent__sort', 'parent__title',)

    def __init__(self, request_data, full_path, categories=None, category=None, selected_filters=[]):
        self.category = category
        self.selected_filters = selected_filters
        super(SimpleProductSearchHandler, self).__init__(request_data, full_path, categories=categories)

    def get_products(self, **kwargs):
        queryset = Product.objects.filter(
            enable=True, categories__in=self.categories,
            categories__enable=True
        )

        selected_filters = list(self.selected_filters)[:]

        if kwargs.get('potential_filter', None):
            selected_filters.append(kwargs.get('potential_filter'))

        key = lambda feature: feature.parent.pk
        iter = groupby(sorted(selected_filters, key=key), key=key)

        for parent, values in iter:
            queryset = queryset.filter(filters__in=map(lambda obj: obj, values))

        return queryset

    def get_queryset(self):
        queryset = super(SimpleProductSearchHandler, self).get_queryset()
        queryset = queryset.filter(enable=True, categories__enable=True)

        selected_filters = list(self.selected_filters)[:]

        key = lambda feature: feature.parent.pk
        iter = groupby(sorted(selected_filters, key=key), key=key)

        for parent, values in iter:
            queryset = queryset.filter(filters__in=map(lambda obj: obj, values))

        queryset = queryset.distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent'),
        )
        return queryset

    def get_search_context_data(self, context_object_name):
        context = super(SimpleProductSearchHandler, self).get_search_context_data(context_object_name)

        context['filters'] = Feature.objects.only(*self.feature_only).filter(
            level=1, filter_products__categories__in=self.categories,
            filter_products__enable=True, filter_products__categories__enable=True
        ).order_by(*self.feature_orders).distinct()

        products = lambda **kwargs: map(lambda obj: obj.id, list(self.get_products(**kwargs)))
        key = lambda feature: feature.parent.pk
        filters_parent = list(groupby(self.selected_filters, key=key))

        for feature in context['filters']:
            feature.potential_products_count = feature.filter_products.filter(
                id__in=products(potential_filter=feature)
            )

            if feature.parent.pk in filters_parent:
                feature.potential_products_count = feature.potential_products_count.exclude(id__in=products)

            feature.potential_products_count = feature.potential_products_count.count()

        return context
