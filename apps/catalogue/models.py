from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from oscar.core.utils import slugify
from mptt.models import MPTTModel, TreeForeignKey
from ckeditor_uploader.fields import RichTextUploadingField
from filer.fields.image import FilerImageField
from django.core.urlresolvers import reverse
from django.utils.translation import get_language, pgettext_lazy
from django.core.cache import cache


class EnableManager(models.Manager):
    def get_queryset(self):
        return super(EnableManager, self).get_queryset().filter(enable=True)


@python_2_unicode_compatible
class Category(MPTTModel):
    name = models.CharField(_('Name'), max_length=300, db_index=True)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=400, unique=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=480)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    description = RichTextUploadingField(_('Description'), blank=True)
    image = FilerImageField(verbose_name=_('Image'), null=True, blank=True, related_name="category_image")
    sort = models.IntegerField(blank=True, null=True, default=0, db_index=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    _slug_separator = '/'
    _full_name_separator = ' > '

    class MPTTMeta:
        order_insertion_by = ('sort', 'name', )

    class Meta:
        ordering = ('sort', 'name', )
        #Todo add index_together like this
        # index_together = (('name', 'slug', ), ('enable', 'created', 'sort', ), )
        unique_together = ('slug', 'parent')
        app_label = 'catalogue'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        if self.pk:
            return self.full_name
        return self.name

    @property
    def full_name(self):
        """
        Returns a string representation of the category and it's ancestors,
        e.g. 'Books > Non-fiction > Essential programming'.

        It's rarely used in Oscar's codebase, but used to be stored as a
        CharField and is hence kept for backwards compatibility. It's also
        sufficiently useful to keep around.
        """
        #Todo category.name to str
        names = [unicode(category.name) for category in self.get_ancestors_and_self()]
        return self._full_name_separator.join(names)

    @property
    def full_slug(self):
        """
        Returns a string of this category's slug concatenated with the slugs
        of it's ancestors, e.g. 'books/non-fiction/essential-programming'.

        Oscar used to store this as in the 'slug' model field, but this field
        has been re-purposed to only store this category's slug and to not
        include it's ancestors' slugs.
        """
        slugs = [category.slug for category in self.get_ancestors_through_parent(include_self=True)]
        return self._slug_separator.join(map(str, slugs))

    def get_ancestors_through_parent(self, include_self=True):
        """
        Get ancestors through the field of the parent.
        :param include_self:
            by default True
            points include the current object in the category list
        :return:
            list of parents
        """
        parents = list()
        parents = self.get_parents(obj=self, parents=parents)

        if include_self is True:
            parents += [self]
        return parents

    def get_meta_title(self):
        return self.meta_title or self.name

    def get_h1(self):
        return self.h1 or self.name

    def get_meta_keywords(self):
        return self.meta_keywords

    def get_meta_description(self):
        return self.meta_description or self.description

    def get_parents(self, obj, parents):
        if obj.parent:
            parents.append(obj.parent)
            return self.get_parents(obj=obj.parent, parents=parents)
        parents.reverse()
        return parents

    def generate_slug(self):
        """
        Generates a slug for a category. This makes no attempt at generating
        a unique slug.
        """
        return slugify(self.name)

    def ensure_slug_uniqueness(self):
        """
        Ensures that the category's slug is unique amongst it's siblings.
        This is inefficient and probably not thread-safe.
        """
        unique_slug = self.slug
        siblings = self.get_siblings().exclude(pk=self.pk)
        next_num = 2
        while siblings.filter(slug=unique_slug).exists():
            unique_slug = '{slug}_{end}'.format(slug=self.slug, end=next_num)
            next_num += 1

        if unique_slug != self.slug:
            self.slug = unique_slug
            self.save()

    def save(self, *args, **kwargs):
        """
        Oscar traditionally auto-generated slugs from names. As that is
        often convenient, we still do so if a slug is not supplied through
        other means. If you want to control slug creation, just create
        instances with a slug already set, or expose a field on the
        appropriate forms.
        """
        if self.slug:
            # Slug was supplied. Hands off!
            super(Category, self).save(*args, **kwargs)
        else:
            self.slug = self.generate_slug()
            super(Category, self).save(*args, **kwargs)
            # We auto-generated a slug, so we need to make sure that it's
            # unique. As we need to be able to inspect the category's siblings
            # for that, we need to wait until the instance is saved. We
            # update the slug and save again if necessary.
            self.ensure_slug_uniqueness()

    def get_ancestors_and_self(self):
        """
        Gets ancestors and includes itself. Use treebeard's get_ancestors
        if you don't want to include the category itself. It's a separate
        function as it's commonly used in templates.
        """
        return list(self.get_ancestors()) + [self]

    def get_descendants_and_self(self):
        """
        Gets descendants and includes itself. Use treebeard's get_descendants
        if you don't want to include the category itself. It's a separate
        function as it's commonly used in templates.
        """
        return list(self.get_descendants()) + [self]

    def has_children(self):
        return self.get_num_children() > 0

    def get_num_children(self):
        return self.get_children().count()

    def get_absolute_url(self):
        """
        Our URL scheme means we have to look up the category's ancestors. As
        that is a bit more expensive, we cache the generated URL. That is
        safe even for a stale cache, as the default implementation of
        ProductCategoryView does the lookup via primary key anyway. But if
        you change that logic, you'll have to reconsider the caching
        approach.
        """
        current_locale = get_language()
        cache_key = 'CATEGORY_URL_%s_%s' % (current_locale, self.pk)
        url = cache.get(cache_key)
        if not url:
            url = reverse(
                'catalogue:category',
                kwargs={'category_slug': self.full_slug, 'pk': self.pk})
            cache.set(cache_key, url)
        return url

    @classmethod
    def get_annotated_list_qs_depth(cls, parent=None, max_depth=None):
        """
        Gets an annotated list from a tree branch, change queryset

        :param parent:

            The node whose descendants will be annotated. The node itself            will be included in the list. If not given, the entire tree
            will be annotated.

        :param max_depth:

            Optionally limit to specified depth

        :sort_order

            Sort order queryset.

        """

        result, info = [], {}
        start_depth, prev_depth = (None, None)
        qs = cls.get_tree(parent)
        if max_depth:
            qs = qs.filter(depth__lte=max_depth)
        return cls.get_annotated_list_qs(qs)

    @classmethod
    def dump_bulk_depth(cls, parent=None, keep_ids=True, max_depth=3):
        """
        Dumps a tree branch to a python type structure.

        Args:
            parent: by default None (if you set the Parent to the object category then we obtain a tree search)
            keep_ids: by default True (if True add id category in data)
            max_depth: by default 3 (max depth in category tree) (if max_depth = 0 return all tree)

        Returns:
        [{'data': category.get_values()},
            {'data': category.get_values(), 'children':[
                {'data': category.get_values()},
                {'data': category.get_values()},
                {'data': category.get_values(), 'children':[
                    {'data': category.get_values()},
                ]},
                {'data': category.get_values()},
            ]},
            {'data': category.get_values()},
            {'data': category.get_values(), 'children':[
                {'data': category.get_values()},
            ]},
        ]
        """
        # Because of fix_tree, this method assumes that the depth
        # and numchild properties in the nodes can be incorrect,
        # so no helper methods are used
        data = cls.get_annotated_list_qs_depth(max_depth=max_depth)
        ret, lnk = [], {}

        for pyobj, info in data:
            # django's serializer stores the attributes in 'fields'
            path = pyobj.path
            depth = int(len(path) / cls.steplen)
            # this will be useless in load_bulk

            newobj = {'data': pyobj.get_values()}

            if keep_ids:
                newobj['id'] = pyobj.pk

            if (not parent and depth == 1) or \
                    (parent and len(path) == len(parent.path)):
                ret.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)
                parentobj = lnk[parentpath]
                if 'children' not in parentobj:
                    parentobj['children'] = []
                parentobj['children'].append(newobj)
            lnk[path] = newobj
        return ret


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
from oscar.apps.catalogue.models import ProductAttributesContainer as CoreProductAttributesContainer


class ProductAttributesContainer(CoreProductAttributesContainer):
    def __getattr__(self, item):
        super(object, self).__getattr__(item)


def init(self, *args, **kwargs):
    super(Product, self).__init__(*args, **kwargs)
    self.attr = ProductAttributesContainer(product=self)


def get_meta_title(self):
    return self.meta_title or self.get_title()


def get_meta_keywords(self):
    return self.meta_keywords


def get_meta_description(self):
    return self.meta_description or self.description


def get_h1(self):
    return self.h1 or self.get_title()


Product.__init__ = init
Product.get_meta_title = get_meta_title
Product.get_meta_description = get_meta_description
Product.get_meta_keywords = get_meta_keywords
Product.get_h1 = get_h1

filters = models.ManyToManyField(
    'catalogue.Feature', related_name="filter_products",
    verbose_name=_('Filters of product'), blank=True
)
filters.contribute_to_class(Product, "filters")
enable = models.BooleanField(verbose_name=_('Enable'), default=True, db_index=True)
enable.contribute_to_class(Product, "enable")

h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
h1.contribute_to_class(Product, "h1")

meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=520)
meta_title.contribute_to_class(Product, "meta_title")

meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
meta_description.contribute_to_class(Product, "meta_description")

meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
meta_keywords.contribute_to_class(Product, "meta_keywords")

