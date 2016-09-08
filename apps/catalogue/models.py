from oscar.apps.catalogue.models import *  # noqa
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


@python_2_unicode_compatible
class Feature(MPTTModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=255, unique=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    sort = models.IntegerField(blank=True, null=True, default=0)
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
