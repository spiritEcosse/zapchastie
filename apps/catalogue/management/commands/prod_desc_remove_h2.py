from django.core.management.base import BaseCommand
from apps.catalogue.models import Product
from bs4 import BeautifulSoup


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """

        for product in Product.objects.all():
            print product
            desc = BeautifulSoup(product.description, 'html5lib')

            if desc.h2:
                desc.h2.decompose()

            while True:
                h2 = desc.find('h2')

                if not h2:
                    break
                h2.name = 'p'

            product.description = desc.prettify()
            product.save()

        self.stdout.write('Successfully write redirects.')
