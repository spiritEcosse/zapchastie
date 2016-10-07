from django.contrib.flatpages.models import FlatPage
from django.contrib import admin
import forms


class FlatPageAdmin(admin.ModelAdmin):
    form = forms.FlatPageForm


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
