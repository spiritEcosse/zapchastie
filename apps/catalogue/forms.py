from django import forms
from dal import autocomplete
from models import Feature
from apps.catalogue.models import Category


class FeatureForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Feature
        widgets = {
            'parent': autocomplete.ModelSelect2(url='feature-autocomplete'),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Category
        widgets = {
            'parent': autocomplete.ModelSelect2(url='categories-autocomplete'),
        }
