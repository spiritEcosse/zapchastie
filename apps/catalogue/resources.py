from import_export import widgets as import_export_widgets
from import_export import resources, fields
import widgets
from oscar.core.loading import get_model
from models import Feature
from filer.models.imagemodels import Image


Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
ProductClass = get_model('catalogue', 'ProductClass')


class ModelResource(resources.ModelResource):
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class CategoryResource(ModelResource):
    parent = fields.Field(
        attribute='parent', widget=import_export_widgets.ForeignKeyWidget(
            model=Category, field='slug',
        )
    )
    image = fields.Field(
        column_name='image', attribute='image',
        widget=widgets.ImageForeignKeyWidget(
            model=Image, field='original_filename'
        )
    )
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Category
        fields = ('id', 'delete', 'enable', 'name', 'slug', 'parent', 'sort', 'meta_title', 'h1', 'meta_description',
                  'meta_keywords', 'description', )
        export_order = fields


class FeatureResource(ModelResource):
    title = fields.Field(column_name='title', attribute='title', widget=widgets.CharWidget())
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'enable', 'title', 'slug', 'parent', 'sort',)
        export_order = fields


class ProductResource(ModelResource):
    filters_slug = fields.Field(
        column_name='filters', attribute='filters',
        widget=widgets.ManyToManyWidget(model=Feature, field='slug')
    )
    parent = fields.Field(
        attribute='parent', column_name='parent',
        widget=import_export_widgets.ForeignKeyWidget(model=Product, field='slug')
    )
    product_class = fields.Field(
        attribute='product_class', column_name='product_class',
        widget=import_export_widgets.ForeignKeyWidget(model=ProductClass, field='slug')
    )
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Product
        fields = ('id', 'delete', 'title', 'slug', 'enable', 'h1', 'meta_title', 'meta_description', 'meta_keywords',
                  'description', 'filters_slug', 'product_class', )
        export_order = fields

