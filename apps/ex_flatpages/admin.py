from django.contrib.flatpages.models import FlatPage
from django.contrib import admin
import forms
from django.utils.translation import ugettext_lazy as _


class FlatPageAdmin(admin.ModelAdmin):
    form = forms.FlatPageForm
    prepopulated_fields = {"url": ("title", )}
    fieldsets = (
        (None, {'fields': ('title', 'url', 'content', 'sites')}),
        (_('Advanced options'), {'classes': ('collapse',),
                                 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
