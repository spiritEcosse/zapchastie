from django.contrib import admin
from models import MetaTags, MetaContent


class MetaTagsAdmin(admin.ModelAdmin):
    list_display = ['page_url', 'meta_title', 'h1']


class MetaContentAdmin(admin.ModelAdmin):
    list_display = ['page_url', 'title']


admin.site.register(MetaTags, MetaTagsAdmin)
admin.site.register(MetaContent, MetaContentAdmin)
