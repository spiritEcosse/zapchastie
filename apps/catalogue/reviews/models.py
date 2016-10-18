from oscar.apps.catalogue.reviews.models import *

ProductReview.default_status = ProductReview.FOR_MODERATION
ProductReview._meta.get_field('status').default = ProductReview.default_status
