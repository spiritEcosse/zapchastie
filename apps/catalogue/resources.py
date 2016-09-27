from import_export import widgets as import_export_widgets
from import_export import resources, fields
import widgets
from oscar.core.loading import get_model
from models import Feature
from filer.models.imagemodels import Image
from django.utils.translation import ugettext_lazy as _
from apps.catalogue.models import Product, Category

ProductClass = get_model('catalogue', 'ProductClass')
ProductImage = get_model('catalogue', 'ProductImage')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')


class ModelResource(resources.ModelResource):
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class CategoryResource(ModelResource):
    parent = fields.Field(
        attribute='parent', column_name='Parent',
        widget=widgets.ForeignKeyWidget(
            model=Category, field='slug',
        )
    )
    image = fields.Field(
        attribute='image', column_name='Image',
        widget=widgets.ForeignKeyWidget(
            model=Image, field='original_filename'
        )
    )
    name = fields.Field(
        attribute='name', column_name='Title',
        widget=widgets.CharWidget()
    )

    class Meta:
        model = Category
        fields = ('id', 'delete', 'enable', 'name', 'slug', 'parent', 'sort', 'meta_title', 'h1', 'meta_description',
                  'meta_keywords', 'description', 'image', )
        export_order = fields


class FeatureResource(ModelResource):
    title = fields.Field(attribute='title', column_name='Title', widget=widgets.CharWidget())
    parent = fields.Field(
        attribute='parent', column_name='Parent',
        widget=widgets.ForeignKeyWidget(
            model=Feature, field='slug'
        )
    )

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'enable', 'title', 'slug', 'parent', 'sort',)
        export_order = fields


class ProductResource(ModelResource):
    filters = fields.Field(
        attribute='filters', column_name='Filters',
        widget=widgets.ManyToManyWidget(model=Feature, field='slug')
    )
    parent = fields.Field(
        attribute='parent', column_name='Parent',
        widget=widgets.ForeignKeyWidget(model=Product, field='slug')
    )
    product_class = fields.Field(
        attribute='product_class', column_name='Class of product',
        widget=widgets.ForeignKeyWidget(model=ProductClass, field='slug')
    )
    title = fields.Field(
        attribute='title', column_name='Title',
        widget=widgets.CharWidget()
    )
    categories = fields.Field(
        attribute='categories', column_name='Categories',
        widget=widgets.ManyToManyWidget(model=Category, field='slug')
    )

    class Meta:
        model = Product
        fields = ('id', 'delete', 'title', 'slug', 'enable', 'h1', 'meta_title', 'meta_description', 'meta_keywords',
                  'description', 'filters', 'categories', 'product_class', 'structure', 'parent', )
        export_order = fields


class ProductImageResource(ModelResource):
    original = fields.Field(
        column_name='original', attribute='original',
        widget=widgets.ForeignKeyWidget(model=Image, field='original_filename')
    )
    product_slug = fields.Field(
        column_name='product', attribute='product',
        widget=widgets.ForeignKeyWidget(model=Product, field='slug')
    )

    class Meta:
        model = ProductImage
        fields = ('id', 'delete', 'product_slug', 'original', 'caption', 'display_order', )
        export_order = fields


class ProductRecommendationResource(ModelResource):
    primary = fields.Field(
        column_name='primary', attribute='primary',
        widget=import_export_widgets.ForeignKeyWidget(
            model=Product, field='slug',
        )
    )
    recommendation = fields.Field(
        column_name='recommendation', attribute='recommendation',
        widget=import_export_widgets.ForeignKeyWidget(
            model=Product, field='slug',
        )
    )

    class Meta:
        model = ProductRecommendation
        fields = ('id', 'delete', 'primary', 'recommendation', 'ranking', )
        export_order = fields

