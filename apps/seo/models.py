from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.models.fields import ExtendedURLField


class MetaTags(models.Model):
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), max_length=480)
    h1 = models.CharField(verbose_name=_('h1'), max_length=310)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'))
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'))
    page_url = ExtendedURLField(_('Page URL'), max_length=128, unique=True, verify_exists=True)

    class Meta:
        verbose_name = _('Meta tags on page')
        verbose_name_plural = _('Meta tags on pages')

    def __str__(self):
        return self.page_url
