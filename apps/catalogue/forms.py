from django import forms
from dal import autocomplete
from models import Feature


class FeatureForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Feature
        widgets = {
            'parent': autocomplete.ModelSelect2(url='feature-autocomplete'),
        }

