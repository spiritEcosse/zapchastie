from import_export import widgets as import_export_widgets
from import_export import resources, fields
import widgets
from oscar.core.loading import get_model
from models import Feature
from filer.models.imagemodels import Image
from django.utils.translation import ugettext_lazy as _
from apps.catalogue.models import Product, Category

ProductClass = get_model('catalogue', 'ProductClass')


class ModelResource(resources.ModelResource):
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class CategoryResource(ModelResource):
    parent = fields.Field(
        attribute='parent', column_name=_('Parent'),
        widget=widgets.ForeignKeyWidget(
            model=Category, field='slug',
        )
    )
    image = fields.Field(
        attribute='image', column_name=_('Image'),
        widget=widgets.ForeignKeyWidget(
            model=Image, field='original_filename'
        )
    )
    name = fields.Field(
        attribute='name', column_name=_('Title'),
        widget=widgets.CharWidget()
    )
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Category
        fields = ('id', 'delete', 'enable', 'name', 'slug', 'parent', 'sort', 'meta_title', 'h1', 'meta_description',
                  'meta_keywords', 'description', 'image', )
        export_order = fields


class FeatureResource(ModelResource):
    title = fields.Field(attribute='title', column_name=_('Title'), widget=widgets.CharWidget())
    parent = fields.Field(
        attribute='parent', column_name=_('Parent'),
        widget=widgets.ForeignKeyWidget(
            model=Feature, field='slug')
    )
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'enable', 'title', 'slug', 'parent', 'sort',)
        export_order = fields


class ProductResource(ModelResource):
    filters = fields.Field(
        attribute='filters', column_name=_('Filters'),
        widget=widgets.ManyToManyWidget(model=Feature, field='slug')
    )
    parent = fields.Field(
        attribute='parent', column_name=_('Parent'),
        widget=widgets.ForeignKeyWidget(model=Product, field='slug')
    )
    product_class = fields.Field(
        attribute='product_class', column_name=_('Class of product'),
        widget=widgets.ForeignKeyWidget(model=ProductClass, field='slug')
    )
    title = fields.Field(
        attribute='title', column_name=_('Title'),
        widget=widgets.CharWidget()
    )
    categories = fields.Field(
        attribute='categories', column_name=_('Categories'),
        widget=widgets.ManyToManyWidget(model=Category, field='slug')
    )
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Product
        fields = ('id', 'delete', 'title', 'slug', 'enable', 'h1', 'meta_title', 'meta_description', 'meta_keywords',
                  'description', 'filters', 'categories', 'product_class', 'structure', 'parent', )
        export_order = fields

