from oscar.apps.partner.admin import *  # noqa
from django.contrib import admin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
from forms import StockRecordForm
from resources import StockRecordResource


class StockRecordAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('product', 'partner', 'price_excl_tax', 'cost_price', 'num_in_stock')
    search_fields = ('product__slug', 'product__id', 'product__title')
    list_filter = ('partner',)
    form = StockRecordForm
    resource_class = StockRecordResource


admin.site.unregister(StockRecord)
admin.site.register(StockRecord, StockRecordAdmin)
