from oscar.apps.promotions.admin import *  # noqa
from django.contrib import admin
import forms


class RawHTMLAdmin(admin.ModelAdmin):
    form = forms.RawHTMLForm


admin.site.unregister(RawHTML)
admin.site.register(RawHTML, RawHTMLAdmin)

