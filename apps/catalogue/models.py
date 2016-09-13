from oscar.apps.catalogue.models import AbstractProduct, ProductAttributesContainer as CoreProductAttributesContainer
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from oscar.core.utils import slugify
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatechars
from auto_parts.settings import TRUNCATECHARS_DESCRIPTION


@python_2_unicode_compatible
class Feature(MPTTModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    slug = models.SlugField(verbose_name=_('Slug'), max_length=255, unique=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    sort = models.IntegerField(verbose_name=_('Sort'), blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)

    class MPTTMeta:
        order_insertion_by = ('sort', 'title', )

    class Meta:
        unique_together = ('slug', 'parent', )
        ordering = ('sort', 'title', )
        verbose_name = _('Feature')
        verbose_name_plural = _('Features')

    def __str__(self):
        if self.parent:
            return u'{} > {}'.format(self.parent, self.title)
        return self.title

    def save(self, *args, **kwargs):
        if not self.sort:
            self.sort = 0

        if not self.slug and self.title:
            self.slug = ''

            if self.parent:
                self.slug = self.parent.slug + '-'
            self.slug += slugify(self.title)

        super(Feature, self).save(*args, **kwargs)


from oscar.apps.catalogue.models import *  # noqa


class ProductAttributesContainer(CoreProductAttributesContainer):
    def __getattr__(self, item):
        super(object, self).__getattr__(item)


def init(self, *args, **kwargs):
    super(AbstractProduct, self).__init__(*args, **kwargs)
    self.attr = ProductAttributesContainer(product=self)


def get_meta_title(self):
    return self.meta_title or self.title


def get_meta_keywords(self):
    return self.meta_keywords


def get_meta_description(self):
    return self.meta_description or truncatechars(strip_tags(self.description), TRUNCATECHARS_DESCRIPTION)


Product.__init__ = init
Product.get_meta_title = get_meta_title
Product.get_meta_description = get_meta_description
Product.get_meta_keywords = get_meta_keywords

filters = models.ManyToManyField(
    'catalogue.Feature', related_name="filter_products",
    verbose_name=_('Filters of product'), blank=True
)
filters.contribute_to_class(Product, "filters")
enable = models.BooleanField(verbose_name=_('Enable'), default=True)
enable.contribute_to_class(Product, "enable")

h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
h1.contribute_to_class(Product, "h1")

meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=520)
meta_title.contribute_to_class(Product, "meta_title")

meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
meta_description.contribute_to_class(Product, "meta_description")

meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
meta_keywords.contribute_to_class(Product, "meta_keywords")
