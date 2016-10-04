from django import forms
from dal import autocomplete
from models import Feature, Category, Product, ProductRecommendation, ProductImage, ProductQuestion
from djng.styling.bootstrap3.forms import Bootstrap3Form
from djng.forms import NgModelFormMixin, NgFormValidationMixin, NgModelForm
from django.utils.translation import ugettext_lazy as _


class ProductQuestionMeta(type(NgModelForm), type(Bootstrap3Form)):
    pass


class ProductQuestionNgForm(NgModelForm, NgModelFormMixin, NgFormValidationMixin, Bootstrap3Form):
    __metaclass__ = ProductQuestionMeta
    scope_prefix = 'product_question'
    form_name = 'product_question_form'

    class Meta:
        model = ProductQuestion
        fields = ('name', 'question', 'email' )
        widgets = {
            'name': forms.TextInput(attrs={'title': _('You name')}),
            'email': forms.TextInput(attrs={'title': _('You email')}),
            'question': forms.Textarea(attrs={'title': _('You question'), 'rows': 5}),
        }
        labels = {
            'name': _('You name'),
            'email': _('You email'),
            'question': _('You question'),
        }
        error_messages = {
            'name': {
                'require': _('Please enter your name.'),
            },
            'email': {
                'require': _('Please enter your email.'),
            },
            'question': {
                'require': _('Please enter your question.')
            }
        }


class ProductQuestionForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
        }


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
        exclude = ('product_class', 'structure', 'parent', 'product_options', )
        widgets = {
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


class ProductImageForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = ProductImage
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
        }


