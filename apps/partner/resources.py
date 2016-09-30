from import_export import fields
from apps.catalogue import widgets
from apps.catalogue.models import Product
from apps.catalogue.resources import ModelResource
from oscar.core.loading import get_model

StockRecord = get_model('partner', 'StockRecord')
Partner = get_model('partner', 'Partner')


class StockRecordResource(ModelResource):
    product_slug = fields.Field(
        column_name='Product', attribute='product',
        widget=widgets.ForeignKeyWidget(model=Product, field='slug')
    )
    partner = fields.Field(
        column_name='Partner', attribute='partner',
        widget=widgets.ForeignKeyWidget(model=Partner, field='code')
    )

    class Meta:
        model = StockRecord
        fields = (
            'id', 'delete', 'product_slug', 'partner', 'price_currency', 'price_excl_tax', 'price_retail',
            'cost_price', 'num_in_stock', 'num_allocated', 'low_stock_threshold',
        )
        export_order = fields
