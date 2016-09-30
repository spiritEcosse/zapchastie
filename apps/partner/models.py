from oscar.apps.partner.abstract_models import AbstractStockRecord
from random import randint
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class StockRecord(AbstractStockRecord):
    def __str__(self):
        msg = u"ProductStockRecord %s of Product: %s" % (
            getattr(self, 'pk', None),
            getattr(self, 'product', None)
        )
        return msg

    def save(self, **kwargs):
        if not self.partner_sku:
            self.partner_sku = randint(1, 1000000000)

        super(StockRecord, self).save(**kwargs)


from oscar.apps.partner.models import *  # noqa
