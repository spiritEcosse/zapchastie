from oscar.apps.partner.admin import *  # noqa
from django.contrib import admin


class StockRecordAdmin(admin.ModelAdmin):
    list_display = ('product', 'partner', 'partner_sku', 'price_excl_tax',
                    'cost_price', 'num_in_stock')
    search_fields = ('product__slug', 'product__id', 'product__title')
    list_filter = ('partner',)


admin.site.unregister(StockRecord)
admin.site.register(StockRecord, StockRecordAdmin)
