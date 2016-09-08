from oscar.apps.catalogue.admin import *  # noqa
from django import forms
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
import resources
import forms
from models import Feature
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from dal import autocomplete
from django.db.models import Q


class FeatureAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeatureAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Feature.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) | Q(slug__icontains=self.q))
        return qs


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'enable', 'slug', 'parent', )
    list_filter = ('created', 'enable', )
    search_fields = ('title', 'slug', 'id', )
    resource_class = resources.FeatureResource
    form = forms.FeatureForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")

admin.site.register(Feature, FeatureAdmin)
