from django.contrib import admin
from models import MetaTags


class MetaTagsAdmin(admin.ModelAdmin):
    list_display = ['page_url', 'meta_title', 'h1']


admin.site.register(MetaTags, MetaTagsAdmin)
