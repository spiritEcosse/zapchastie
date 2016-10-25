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
from oscar.models.fields import AutoSlugField, NullCharField
from oscar.core.loading import get_classes
from oscar.core.decorators import deprecated
from django.utils.functional import cached_property
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.template import loader, Context
from django.conf import settings
import os
from auto_parts.settings import MEDIA_ROOT
from django.template.defaultfilters import truncatechars
from django.contrib.auth.models import User
from django.contrib.staticfiles.finders import find
import logging
import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.finders import find
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Count, Sum
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language, pgettext_lazy

from treebeard.mp_tree import MP_Node

from oscar.core.decorators import deprecated
from oscar.core.loading import get_class, get_classes, get_model
from oscar.core.utils import slugify
from oscar.core.validators import non_python_keyword
from oscar.models.fields import AutoSlugField, NullCharField
from wand.image import Image as WandImage
from filer.models.imagemodels import Image
from auto_parts.settings import WATERMARK, SHOP_NAME
from django.contrib.sites.models import Site
from wand.compat import nested
ProductManager, BrowsableProductManager = get_classes(
    'catalogue.managers', ['ProductManager', 'BrowsableProductManager'])


class EnableManager(models.Manager):
    def get_queryset(self):
        return super(EnableManager, self).get_queryset().filter(enable=True)


def get_product_class():
    try:
        product_class = ProductClass.objects.get(slug='obshchii')
    except ProductClass.DoesNotExist:
        product_class = ProductClass.objects.create(requires_shipping=False, track_stock=False, name='obshchii')

    return product_class


def create_img_wm(source):
    position = lambda param: getattr(background, param) / 2 - getattr(watermark, param) / 2

    with nested(WandImage(filename=source.path), WandImage(filename=WATERMARK['image'])) as (background, watermark):
        file_path, file_extension = os.path.splitext(source.path)
        image_wm = u'{}_{}{}'.format(file_path, SHOP_NAME, file_extension)

        background.watermark(
            image=watermark, transparency=WATERMARK['transparency'], left=position('width'), top=position('height')
        )

        background.save(filename=image_wm)
    return {'original': os.path.relpath(image_wm, start='media')}


class CommonFeatureProduct(object):
    @property
    def product_slug(self):
        return self.product.slug

    def product_enable(self):
        return self.product.enable
    product_enable.short_description = _('Enable product')

    def product_categories_to_str(self):
        return self.product.product_categories_to_str()
    product_categories_to_str.short_description = _("Categories")

    def partners_to_str(self):
        return self.product.partners_to_str()
    partners_to_str.short_description = _("Partner")

    def thumb(self, image=None):
        if not image:
            image = self.product.primary_image()

        return loader.get_template(
            'admin/catalogue/product/thumb.html'
        ).render(
            Context(
                {
                    'image': image
                }
            )
        )
    thumb.allow_tags = True
    thumb.short_description = _('Image of product')

    def product_date_updated(self):
        return self.product.date_updated
    product_date_updated.short_description = _("Product date updated")


@python_2_unicode_compatible
class Feature(MPTTModel):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    slug = models.SlugField(verbose_name=_('Slug'), max_length=255, unique=True, blank=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    sort = models.IntegerField(verbose_name=_('Sort'), blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    slug_separator = '/'

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

    def get_absolute_url(self, values={}):
        dict_values = {'category_slug': self.full_slug}

        if values.get('filter_slug_objects'):
            filter_slug = values.get('filter_slug_objects').values_list('slug', flat=True)
            filter_slug = Feature.slug_separator.join(filter_slug)

            dict_values.update(
                {
                    'filter_slug': filter_slug
                }
            )

        return reverse('catalogue:category', kwargs=dict_values)


@python_2_unicode_compatible
class ProductImage(models.Model, CommonFeatureProduct):
    """
    An image of a product
    """
    product = models.ForeignKey(
        'catalogue.Product', related_name='images', verbose_name=_("Product"))
    original = FilerImageField(verbose_name=_("Original"), null=True, blank=True, related_name="original")
    caption = models.CharField(_("Caption"), max_length=200, blank=True)

    #: Use display_order to determine which is the "primary" image
    display_order = models.PositiveIntegerField(
        _("Display order"), default=0,
        help_text=_("An image with a display order of zero will be the primary"
                    " image for a product"))
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        app_label = 'catalogue'
        # Any custom models should ensure that this ordering is unchanged, or
        # your query count will explode. See AbstractProduct.primary_image.
        ordering = ["display_order"]
        unique_together = ("product", "display_order")
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')

    def __str__(self):
        return u"Image of '%s'" % getattr(self, 'product', None)

    @property
    def name(self):
        return self.original.file.name if self.original else ''

    @property
    def image(self):
        return create_img_wm(source=self.exist_image())

    @property
    def admin_image(self):
        return self.exist_image()

    def exist_image(self):
        current_path = os.getcwd()
        os.chdir(MEDIA_ROOT)
        abs_path = os.path.abspath(self.name)
        image = self

        if not self.name or not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            image = self.product.get_missing_image()

        os.chdir(current_path)
        return image

    @property
    def path(self):
        return self.original.path

    def is_primary(self):
        """
        Return bool if image display order is 0
        """
        return self.display_order == 0

    def thumb(self, image=None):
        return super(ProductImage, self).thumb(image=self.admin_image)

    def delete(self, *args, **kwargs):
        """
        Always keep the display_order as consecutive integers. This avoids
        issue #855.
        """
        images = self.product.images.all().exclude(pk=self.pk)

        super(ProductImage, self).delete(*args, **kwargs)

        for idx, image in enumerate(images):
            image.display_order = idx
            image.save()


from oscar.apps.catalogue.abstract_models import ProductAttributesContainer, AbstractProductRecommendation


class ProductRecommendation(AbstractProductRecommendation, CommonFeatureProduct):
    def __init__(self, *args, **kwargs):
        super(ProductRecommendation, self).__init__(*args, **kwargs)
        self.product = getattr(self, 'primary', None)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.ranking is None:
            self.ranking = 0

        super(ProductRecommendation, self).save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )

    def recommendation_thumb(self):
        return self.recommendation.thumb()
    recommendation_thumb.allow_tags = True
    recommendation_thumb.short_description = _('Image of recommendation product.')


class MissingProductImage(object):

    """
    Mimics a Django file field by having a name property.

    sorl-thumbnail requires all it's images to be in MEDIA_ROOT. This class
    tries symlinking the default "missing image" image in STATIC_ROOT
    into MEDIA_ROOT for convenience, as that is necessary every time an Oscar
    project is setup. This avoids the less helpful NotFound IOError that would
    be raised when sorl-thumbnail tries to access it.
    """

    def __init__(self, name=None):
        self.name = name if name else settings.OSCAR_MISSING_IMAGE_URL
        self.media_file_path = os.path.join(settings.MEDIA_ROOT, self.name)
        # don't try to symlink if MEDIA_ROOT is not set (e.g. running tests)
        if settings.MEDIA_ROOT and not os.path.exists(self.media_file_path):
            self.symlink_missing_image(self.media_file_path)

    @property
    def is_missing(self):
        return True

    @property
    def path(self):
        return self.media_file_path

    @property
    def original(self):
        return self.name

    def symlink_missing_image(self, media_file_path):
        static_file_path = find('oscar/img/%s' % self.name)
        if static_file_path is not None:
            try:
                os.symlink(static_file_path, media_file_path)
            except OSError:
                raise ImproperlyConfigured((
                    "Please copy/symlink the "
                    "'missing image' image at %s into your MEDIA_ROOT at %s. "
                    "This exception was raised because Oscar was unable to "
                    "symlink it for you.") % (media_file_path,
                                              settings.MEDIA_ROOT))
            else:
                logging.info((
                    "Symlinked the 'missing image' image at %s into your "
                    "MEDIA_ROOT at %s") % (media_file_path,
                                           settings.MEDIA_ROOT))


class ProductAttributesContainerCustom(ProductAttributesContainer):
    def __getattr__(self, item):
        super(object, self).__getattr__(item)


@python_2_unicode_compatible
class Product(models.Model, CommonFeatureProduct):
    """
    The base product object

    There's three kinds of products; they're distinguished by the structure
    field.

    - A stand alone product. Regular product that lives by itself.
    - A child product. All child products have a parent product. They're a
      specific version of the parent.
    - A parent product. It essentially represents a set of products.

    An example could be a yoga course, which is a parent product. The different
    times/locations of the courses would be associated with the child products.
    """
    STANDALONE, PARENT, CHILD = 'standalone', 'parent', 'child'
    STRUCTURE_CHOICES = (
        (STANDALONE, _('Stand-alone product')),
        (PARENT, _('Parent product')),
        (CHILD, _('Child product'))
    )
    structure = models.CharField(
        _("Product structure"), max_length=10, choices=STRUCTURE_CHOICES,
        default=STANDALONE)

    upc = NullCharField(
        _("UPC"), max_length=64, blank=True, null=True, unique=True,
        help_text=_("Universal Product Code (UPC) is an identifier for "
                    "a product which is not specific to a particular "
                    " supplier. Eg an ISBN for a book."))

    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        verbose_name=_("Parent product"),
        help_text=_("Only choose a parent product if you're creating a child "
                    "product.  For example if this is a size "
                    "4 of a particular t-shirt.  Leave blank if this is a "
                    "stand-alone product (i.e. there is only one version of"
                    " this product)."))

    # Title is mandatory for canonical products but optional for child products
    title = models.CharField(pgettext_lazy(u'Product title', u'Title'),
                             max_length=255, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=520)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    description = RichTextUploadingField(_('Description'), blank=True)

    #: "Kind" of product, e.g. T-Shirt, Book, etc.
    #: None for child products, they inherit their parent's product class
    product_class = models.ForeignKey(
        'catalogue.ProductClass', null=True, blank=True, on_delete=models.PROTECT,
        verbose_name=_('Product type'), related_name="products",
        help_text=_("Choose what type of product this is"))
    attributes = models.ManyToManyField(
        'catalogue.ProductAttribute',
        through='ProductAttributeValue',
        verbose_name=_("Attributes"),
        help_text=_("A product attribute is something that this product may "
                    "have, such as a size, as specified by its class"))
    #: It's possible to have options product class-wide, and per product.
    product_options = models.ManyToManyField(
        'catalogue.Option', blank=True, verbose_name=_("Product options"),
        help_text=_("Options are values that can be associated with a item "
                    "when it is added to a customer's basket.  This could be "
                    "something like a personalised message to be printed on "
                    "a T-shirt."))

    recommended_products = models.ManyToManyField(
        'catalogue.Product', through='ProductRecommendation', blank=True,
        verbose_name=_("Recommended products"),
        help_text=_("These are products that are recommended to accompany the "
                    "main product."))

    # Denormalised product rating - used by reviews app.
    # Product has no ratings if rating is None
    rating = models.FloatField(_('Rating'), null=True, editable=False)

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    # This field is used by Haystack to reindex search
    date_updated = models.DateTimeField(
        _("Date updated"), auto_now=True, db_index=True)

    categories = models.ManyToManyField('catalogue.Category', related_name="products", verbose_name=_("Categories"))

    filters = models.ManyToManyField(
        'catalogue.Feature', related_name="filter_products",
        verbose_name=_('Filters of product'), blank=True
    )

    #: Determines if a product may be used in an offer. It is illegal to
    #: discount some types of product (e.g. ebooks) and this field helps
    #: merchants from avoiding discounting such products
    #: Note that this flag is ignored for child products; they inherit from
    #: the parent product.
    is_discountable = models.BooleanField(
        _("Is discountable?"), default=True, help_text=_(
            "This flag indicates if this product can be used in an offer "
            "or not"))

    enable = models.BooleanField(verbose_name=_('Enable'), default=True, db_index=True)
    objects = ProductManager()
    browsable = BrowsableProductManager()
    separator = ','

    class Meta:
        app_label = 'catalogue'
        ordering = ['-date_created']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.attr = ProductAttributesContainerCustom(product=self)

    def __str__(self):
        if self.title:
            return self.title
        if self.attribute_summary:
            return u"%s (%s)" % (self.get_title(), self.attribute_summary)
        else:
            return self.get_title()

    def get_absolute_url(self):
        """
        Return a product's absolute url
        """
        return reverse('catalogue:detail', kwargs={'product_slug': self.slug})

    def clean(self):
        """
        Validate a product. Those are the rules:

        +---------------+-------------+--------------+--------------+
        |               | stand alone | parent       | child        |
        +---------------+-------------+--------------+--------------+
        | title         | required    | required     | optional     |
        +---------------+-------------+--------------+--------------+
        | product class | required    | required     | must be None |
        +---------------+-------------+--------------+--------------+
        | parent        | forbidden   | forbidden    | required     |
        +---------------+-------------+--------------+--------------+
        | stockrecords  | 0 or more   | forbidden    | 0 or more    |
        +---------------+-------------+--------------+--------------+
        | categories    | 1 or more   | 1 or more    | forbidden    |
        +---------------+-------------+--------------+--------------+
        | attributes    | optional    | optional     | optional     |
        +---------------+-------------+--------------+--------------+
        | rec. products | optional    | optional     | unsupported  |
        +---------------+-------------+--------------+--------------+
        | options       | optional    | optional     | forbidden    |
        +---------------+-------------+--------------+--------------+

        Because the validation logic is quite complex, validation is delegated
        to the sub method appropriate for the product's structure.
        """
        self.save_deffer_fields()

        getattr(self, '_clean_%s' % self.structure)()
        if not self.is_parent:
            self.attr.validate_attributes()

    def save_deffer_fields(self):
        if not self.slug and self.title:
            self.slug = slugify(self.title)

        if not self.product_class:
            self.product_class = get_product_class()

        if not self.structure:
            self.structure = self.STANDALONE

    def _clean_standalone(self):
        """
        Validates a stand-alone product
        """
        if not self.title:
            raise ValidationError(_("Your product must have a title."))
        if not self.product_class:
            raise ValidationError(_("Your product must have a product class."))
        if self.parent_id:
            raise ValidationError(_("Only child products can have a parent."))

    def _clean_child(self):
        """
        Validates a child product
        """
        if not self.parent_id:
            raise ValidationError(_("A child product needs a parent."))
        if self.parent_id and not self.parent.is_parent:
            raise ValidationError(
                _("You can only assign child products to parent products."))
        if self.product_class:
            raise ValidationError(
                _("A child product can't have a product class."))
        if self.pk and self.categories.exists():
            raise ValidationError(
                _("A child product can't have a category assigned."))
        # Note that we only forbid options on product level
        if self.pk and self.product_options.exists():
            raise ValidationError(
                _("A child product can't have options."))

    def _clean_parent(self):
        """
        Validates a parent product.
        """
        self._clean_standalone()
        if self.has_stockrecords:
            raise ValidationError(
                _("A parent product can't have stockrecords."))

    def save(self, *args, **kwargs):
        self.save_deffer_fields()

        super(Product, self).save(*args, **kwargs)
        self.attr.save()

    # Properties

    @property
    def is_standalone(self):
        return self.structure == self.STANDALONE

    @property
    def is_parent(self):
        return self.structure == self.PARENT

    @property
    def is_child(self):
        return self.structure == self.CHILD

    def can_be_parent(self, give_reason=False):
        """
        Helps decide if a the product can be turned into a parent product.
        """
        reason = None
        if self.is_child:
            reason = _('The specified parent product is a child product.')
        if self.has_stockrecords:
            reason = _(
                "One can't add a child product to a product with stock"
                " records.")
        is_valid = reason is None
        if give_reason:
            return is_valid, reason
        else:
            return is_valid

    @property
    def options(self):
        """
        Returns a set of all valid options for this product.
        It's possible to have options product class-wide, and per product.
        """
        pclass_options = self.get_product_class().options.all()
        return set(pclass_options) or set(self.product_options.all())

    @property
    def is_shipping_required(self):
        return self.get_product_class().requires_shipping

    @property
    def has_stockrecords(self):
        """
        Test if this product has any stockrecords
        """
        return self.stockrecords.exists()

    @property
    def num_stockrecords(self):
        return self.stockrecords.count()

    @property
    def attribute_summary(self):
        """
        Return a string of all of a product's attributes
        """
        attributes = self.attribute_values.all()
        pairs = [attribute.summary() for attribute in attributes]
        return ", ".join(pairs)

    # The two properties below are deprecated because determining minimum
    # price is not as trivial as it sounds considering multiple stockrecords,
    # currencies, tax, etc.
    # The current implementation is very naive and only works for a limited
    # set of use cases.
    # At the very least, we should pass in the request and
    # user. Hence, it's best done as an extension to a Strategy class.
    # Once that is accomplished, these properties should be removed.

    @property
    @deprecated
    def min_child_price_incl_tax(self):
        """
        Return minimum child product price including tax.
        """
        return self._min_child_price('incl_tax')

    @property
    @deprecated
    def min_child_price_excl_tax(self):
        """
        Return minimum child product price excluding tax.

        This is a very naive approach; see the deprecation notice above. And
        only use it for display purposes (e.g. "new Oscar shirt, prices
        starting from $9.50").
        """
        return self._min_child_price('excl_tax')

    def _min_child_price(self, prop):
        """
        Return minimum child product price.

        This is for visual purposes only. It ignores currencies, most of the
        Strategy logic for selecting stockrecords, knows nothing about the
        current user or request, etc. It's only here to ensure
        backwards-compatibility; the previous implementation wasn't any
        better.
        """
        strategy = Selector().strategy()

        children_stock = strategy.select_children_stockrecords(self)
        prices = [
            strategy.pricing_policy(child, stockrecord)
            for child, stockrecord in children_stock]
        raw_prices = sorted([getattr(price, prop) for price in prices])
        return raw_prices[0] if raw_prices else None

    # Wrappers for child products

    def get_title(self):
        """
        Return a product's title or it's parent's title if it has no title
        """
        title = self.title
        if not title and self.parent_id:
            title = self.parent.title
        return title
    get_title.short_description = pgettext_lazy(u"Product title", u"Title")

    def get_meta_title(self):
        return self.meta_title or self.get_title()

    def get_meta_keywords(self):
        return self.meta_keywords

    def get_meta_description(self):
        return self.meta_description or self.description

    def get_h1(self):
        return self.h1 or self.get_title()

    def get_product_class(self):
        """
        Return a product's item class. Child products inherit their parent's.
        """
        if self.is_child:
            return self.parent.product_class
        else:
            return self.product_class
    get_product_class.short_description = _("Product class")

    def product_categories_to_str(self):
        return self.separator.join([category.name for category in self.get_categories().all()])
    product_categories_to_str.short_description = _("Categories")

    def partners_to_str(self):
        return self.separator.join([stockrecord.partner.name for stockrecord in self.stockrecords.all()])
    partners_to_str.short_description = _("Partners")

    def get_is_discountable(self):
        """
        At the moment, is_discountable can't be set individually for child
        products; they inherit it from their parent.
        """
        if self.is_child:
            return self.parent.is_discountable
        else:
            return self.is_discountable

    def get_categories(self):
        """
        Return a product's categories or parent's if there is a parent product.
        """
        if self.is_child:
            return self.parent.categories
        else:
            return self.categories
    get_categories.short_description = _("Categories")

    # Images

    def images_all(self):
        images = [image.image for image in self.images.all()]
        images = filter(lambda image: getattr(image, 'is_missing', False) is False, images)
        return [self.get_missing_image()] if not images else images

    def get_missing_image(self):
        """
        Returns a missing image object.
        """
        # This class should have a 'name' property so it mimics the Django file
        # field.
        return MissingProductImage()

    def thumb(self, image=None):
        image = self.images.all()[0].admin_image if self.images.all() else self.get_missing_image()
        return super(Product, self).thumb(image=image)

    def primary_image(self):
        """
        Returns the primary image for a product. Usually used when one can
        only display one product image, e.g. in a list of products.
        """
        return self.images.all()[0].image if self.images.all() else self.get_missing_image()

    # Updating methods

    def update_rating(self):
        """
        Recalculate rating field
        """
        self.rating = self.calculate_rating()
        self.save()
    update_rating.alters_data = True

    def calculate_rating(self):
        """
        Calculate rating value
        """
        result = self.reviews.filter(
            status=self.reviews.model.APPROVED
        ).aggregate(
            sum=Sum('score'), count=Count('id'))
        reviews_sum = result['sum'] or 0
        reviews_count = result['count'] or 0
        rating = None
        if reviews_count > 0:
            rating = float(reviews_sum) / reviews_count
        return rating

    def has_review_by(self, user):
        if user.is_anonymous():
            return False
        return self.reviews.filter(user=user).exists()

    def is_review_permitted(self, user):
        """
        Determines whether a user may add a review on this product.

        Default implementation respects OSCAR_ALLOW_ANON_REVIEWS and only
        allows leaving one review per user and product.

        Override this if you want to alter the default behaviour; e.g. enforce
        that a user purchased the product to be allowed to leave a review.
        """
        if user.is_authenticated() or settings.OSCAR_ALLOW_ANON_REVIEWS:
            return not self.has_review_by(user)
        else:
            return False

    def get_approved_reviews(self):
        return self.reviews.filter(status=self.reviews.model.APPROVED)

    @cached_property
    def num_approved_reviews(self):
        return self.reviews.filter(
            status=self.reviews.model.APPROVED).count()


from oscar.apps.catalogue.models import *  # noqa


@python_2_unicode_compatible
class ProductQuestion(models.Model):
    name = models.CharField(verbose_name=_('User name'), max_length=100)
    email = models.EmailField(verbose_name=_('User email'))
    question = models.TextField(verbose_name=_('Question about the product'))
    product = models.ForeignKey(Product, verbose_name=_('Product'))
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True)
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        verbose_name = _('Question about the product')
        verbose_name_plural = _('Questions about the products')
        ordering = ('product', )

    def __str__(self):
        return u'Question "{}" of product {}'.format(truncatechars(self.question, 50), self.product)

    def get_email(self):
        return self.user.email or self.email
    get_email.short_description = _('User email')

    def get_name(self):
        return self.user.username or self.name
    get_name.short_description = _('User name')
