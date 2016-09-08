from oscar.apps.catalogue.admin import *  # noqa
from django import forms
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
import resources
import forms


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'slug', 'parent', )
    list_filter = ('created', )
    search_fields = ('title', 'slug', 'id', )
    resource_class = resources.FeatureResource
    form = forms.FeatureForm

    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")

