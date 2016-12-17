from apps.catalogue.reviews.abstract_models import AbstractProductReview
from django.core.urlresolvers import reverse


class ProductReview(AbstractProductReview):
    def save(self, *args, **kwargs):
        super(ProductReview, self).save()

        if getattr(self, 'product', False):
            self.product.update_rating()

    def get_absolute_url(self):
        kwargs = {'pk': self.id}

        if getattr(self, 'product', False):
            kwargs.update({
                'product_slug': self.product.slug,
            })

        return reverse('catalogue:reviews-detail', kwargs=kwargs)


from oscar.apps.catalogue.reviews.models import *

ProductReview.default_status = ProductReview.FOR_MODERATION
ProductReview._meta.get_field('status').default = ProductReview.default_status
ProductReview._meta.get_field('product').blank = True
