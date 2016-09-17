from oscar.apps.catalogue.admin import *  # noqa
from django import forms
from mptt.admin import DraggableMPTTAdmin
from treebeard.admin import TreeAdmin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
import resources
import forms
from models import Feature
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from dal import autocomplete
from django.db.models import Q
from oscar.core.loading import get_model
from django.db.models.query import Prefetch
from django.forms import Textarea
from django.db import models


Product = get_model('catalogue', 'Product')


class FeatureAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeatureAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Feature.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) | Q(slug__icontains=self.q))
        return qs


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'enable', 'slug', 'parent', )
    list_filter = ('created', 'enable', )
    search_fields = ('title', 'slug', 'id', )
    resource_class = resources.FeatureResource
    form = forms.FeatureForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class ProductAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'title', 'enable', 'date_updated', 'slug', 'structure', 'attribute_summary', )
    list_filter = ('enable', 'date_updated', 'categories__name', 'structure', 'is_discountable', )
    inlines = (ProductRecommendationInline, )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', 'id', )
    # form = forms.ProductForm
    resource_class = resources.ProductResource
    list_select_related = ('product_class', )
    list_attr = ('pk', 'title', 'enable', 'date_updated', 'slug', 'structure', 'product_class__name', )

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return qs.only(*self.list_attr).order_by('-date_updated', 'title').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.only('original', 'product')),
            Prefetch('attribute_values'),
            Prefetch('attributes'),
        )


class CategoryAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    prepopulated_fields = {'slug': ("name",)}
    list_display = ('pk', 'indented_title', 'slug', 'enable', 'parent', 'sort', 'created')
    list_filter = ('enable', 'created', )
    formfield_overrides = {
        models.TextField: {'widget': Textarea()},
    }
    search_fields = ('name', 'slug', 'id',)
    resource_class = resources.CategoryResource
    # form = forms.CategoryForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


admin.site.register(Feature, FeatureAdmin)
admin.site.unregister(Product)
admin.site.register(Product, ProductAdmin)
admin.site.unregister(Category)
admin.site.register(Category, CategoryAdmin)
