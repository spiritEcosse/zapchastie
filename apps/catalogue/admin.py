from oscar.apps.catalogue.admin import *  # noqa
from django import forms
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
import resources
import forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from dal import autocomplete
from django.db.models import Q
from django.db.models.query import Prefetch
from django.forms import Textarea
from django.db import models
from models import Feature, Product, ProductImage, ProductQuestion
from apps.partner.models import StockRecord
from apps.partner.forms import StockRecordForm


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProductAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Product.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(title__iexact=self.q) | Q(slug__iexact=self.q))
            else:
                qs = qs.filter(pk=self.q)

        return qs


class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CategoriesAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Category.objects.all().only('pk', 'name', 'slug', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(name__iexact=self.q) | Q(slug__iexact=self.q))
            else:
                qs = qs.filter(pk=self.q)

        return qs


class FeatureAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeatureAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Feature.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(title__iexact=self.q) | Q(slug__iexact=self.q))
            else:
                qs = qs.filter(pk=self.q)

        return qs


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class StockRecordInline(admin.StackedInline):
    model = StockRecord
    form = StockRecordForm


class ProductRecommendationInline(admin.TabularInline):
    model = ProductRecommendation
    fk_name = 'primary'
    form = forms.ProductRecommendationForm


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'slug', 'parent', )
    list_filter = ('created', )
    search_fields = ('title', 'slug', 'id', )
    resource_class = resources.FeatureResource
    form = forms.FeatureForm
    list_select_related = ('parent', )


class ProductAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = (
        'pk', 'title', 'enable', 'slug', 'thumb', 'date_updated', 'product_categories_to_str', 'partners_to_str',
    )
    list_filter = ('enable', 'date_updated', 'categories__name', 'is_discountable', )
    inlines = (ProductRecommendationInline, ProductImageInline, StockRecordInline, )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', 'id', )
    form = forms.ProductForm
    resource_class = resources.ProductResource
    list_attr = ('pk', 'title', 'enable', 'date_updated', 'slug', )

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return qs.only(*self.list_attr).order_by('-date_updated', 'title').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.only('original', 'product')),
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
    form = forms.CategoryForm
    list_select_related = ('parent', )


class ProductImageAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = resources.ProductImageResource
    list_display = ('pk', 'thumb', 'product', 'product_slug', 'product_date_updated', 'display_order', 'caption',
                    'product_enable', 'product_categories_to_str', 'partners_to_str', 'date_created', )
    list_filter = ('date_created', 'product__date_updated', 'product__enable', 'product__stockrecords__partner',
                   'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__id', )
    form = forms.ProductImageForm
    list_select_related = ('product', )

    def get_queryset(self, request):
        qs = super(ProductImageAdmin, self).get_queryset(request)
        return qs.prefetch_related(
            Prefetch('product__categories'),
            Prefetch('product__stockrecords__partner'),
        )


class ProductRecommendationAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'primary', 'product_slug', 'product_enable', 'thumb', 'product_date_updated',
                    'product_categories_to_str', 'partners_to_str', 'recommendation', 'recommendation_thumb',
                    'ranking',)
    list_filter = ('primary__date_updated', 'primary__enable', 'primary__stockrecords__partner',
                   'primary__categories', )
    search_fields = ('primary__title', 'primary__slug', 'primary__pk', )
    resource_class = resources.ProductRecommendationResource
    form = forms.ProductRecommendationForm


class ProductQuestionAdmin(admin.ModelAdmin):
    form = forms.ProductQuestionForm


admin.site.register(Feature, FeatureAdmin)
admin.site.register(ProductQuestion, ProductQuestionAdmin)
admin.site.unregister(Product)
admin.site.register(Product, ProductAdmin)
admin.site.unregister(Category)
admin.site.register(Category, CategoryAdmin)
admin.site.unregister(ProductImage)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductRecommendation, ProductRecommendationAdmin)
admin.site.unregister(ProductAttribute)
admin.site.unregister(ProductClass)
admin.site.unregister(ProductAttributeValue)
admin.site.unregister(AttributeOptionGroup)
admin.site.unregister(Option)
admin.site.unregister(ProductCategory)
