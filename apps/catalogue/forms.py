from django import forms
from dal import autocomplete
from models import Feature
from apps.catalogue.models import Category, Product, ProductRecommendation


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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'parent': autocomplete.ModelSelect2(url='product-autocomplete'),
            'filters': autocomplete.ModelSelect2Multiple(url='feature-autocomplete'),
            'categories': autocomplete.ModelSelect2Multiple(url='categories-autocomplete'),
        }


class ProductRecommendationForm(forms.ModelForm):
    class Meta:
        model = ProductRecommendation
        fields = '__all__'
        widgets = {
            'recommendation': autocomplete.ModelSelect2(url='product-autocomplete'),
            'primary': autocomplete.ModelSelect2(url='product-autocomplete')
        }

