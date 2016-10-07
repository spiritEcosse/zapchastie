from models import RawHTML
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class RawHTMLForm(forms.ModelForm):
    class Meta:
        model = RawHTML
        fields = '__all__'
        widgets = {
            'body': CKEditorUploadingWidget()
        }
