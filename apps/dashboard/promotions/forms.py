from django import forms
from oscar.core.loading import get_class

RawHTML = get_class('promotions.models', 'RawHTML')


class RawHTMLForm(forms.ModelForm):
    class Meta:
        model = RawHTML
        fields = ['name', 'body']
