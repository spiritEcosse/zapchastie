from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.models.fields import PhoneNumberField


@python_2_unicode_compatible
class Info(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='info')
    phone_numbers = models.ManyToManyField('ex_sites.PhoneNumber', verbose_name=_('Phone numbers'), blank=True)
    email = models.EmailField(verbose_name=_('Email'), max_length=200)
    shop_short_desc = models.CharField(verbose_name=_('Short description of shop'), max_length=200, blank=True)

    def __str__(self):
        return self.site.domain

    class Meta:
        verbose_name = _('Information')
        verbose_name_plural = _('Information')


class PhoneNumber(models.Model):
    phone_number = PhoneNumberField(verbose_name=_('Phone number'), blank=True)
