from oscar.core.loading import get_model
from django import forms
from dal import autocomplete

StockRecord = get_model('partner', 'StockRecord')


class StockRecordForm(forms.ModelForm):
    class Meta:
        exclude = ('partner_sku', )
        model = StockRecord
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
        }
