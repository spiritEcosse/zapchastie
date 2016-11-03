from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
import urllib2, urllib
from bs4 import BeautifulSoup
from apps.catalogue.models import Category, Product, ProductImage, Feature, ProductClass
from apps.partner.models import StockRecord, Partner
import os
from django.contrib.auth.models import User
from django.core.files import File
from filer.models import Image
from decimal import Decimal
import random
from django.db.utils import IntegrityError
from oscar.core.utils import slugify
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict

timeout = 30

current_site = Site.objects.get(pk=1)
TRUNCATE_LINK = 24

product_class, created = ProductClass.objects.get_or_create(requires_shipping=False, track_stock=False, name='obshchii')
partner, created = Partner.objects.get_or_create(name='partner', code='partner')


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        # Redirect.objects.all().delete()
        # Feature.objects.all().delete()
        # Image.objects.all().delete()
        # Category.objects.all().delete()
        # StockRecord.objects.all().delete()
        # ProductImage.objects.all().delete()
        # Product.objects.all().delete()

        url = 'http://zapchastie.com.ua/'
        request = urllib2.Request(url)
        request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
        main_page = urllib2.urlopen(request, timeout=timeout)
        soup_main_page = BeautifulSoup(main_page.read(), 'html5lib')
        categories = soup_main_page.select('#menu .navbar-ex1-collapse .navbar-nav > li > a')

        for category_html in categories:
            category_link = category_html.attrs['href'].encode(encoding='UTF-8', errors='strict')
            category_page_soup = self.save_category(category_link, True)

            pages = category_page_soup.select('.pagination a')

            for page in pages[:-2]:
                category_link = page.attrs['href'].encode(encoding='UTF-8', errors='strict')
                self.save_category(category_link)

        self.stdout.write('Successfully write redirects.')

    def save_category(self, category_link, page=False, parent_category=None):
        relative_path = category_link[TRUNCATE_LINK:]
        print 'category =================='
        print 'parent_category', parent_category
        print relative_path, '\n'

        request = urllib2.Request(category_link)
        request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
        category_page = urllib2.urlopen(request, timeout=timeout)
        category_page_soup = BeautifulSoup(category_page.read(), 'html5lib')
        meta_description = category_page_soup.find(attrs={"name": "description"})
        meta_keywords = category_page_soup.find(attrs={"name": "keywords"})

        try:
            category, created = Category.objects.get_or_create(
                name=category_page_soup.h1.string, parent=parent_category
            )
        except IntegrityError:
            category = Category.objects.create(
                name=category_page_soup.h1.string,
                parent=parent_category,
                slug=slugify('{}-{}'.format(
                    slugify(category_page_soup.h1.string),
                    Category.objects.order_by('-id').first().pk + 1)
                )
            )

        category.meta_title = category_page_soup.title.string
        category.h1 = category_page_soup.h1.string
        category.meta_description = meta_description.get('content') if meta_description else ''
        category.meta_keywords = meta_keywords.get('content') if meta_keywords else ''
        category.description = u' '.join(map(unicode, category_page_soup.find('div', 'col-sm-10').contents))
        category.save()

        products = category_page_soup.select('#content .product-thumb > .image > a')

        # print 'Products ========================'
        for product_html in products:
            product_link = product_html.attrs['href'].encode(encoding='UTF-8', errors='strict')
            # print product_link

            request = urllib2.Request(product_link)
            request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
            product_page = urllib2.urlopen(request, timeout=timeout)
            product_page_soup = BeautifulSoup(product_page.read(), 'html5lib')
            meta_description = product_page_soup.find(attrs={"name": "description"})
            meta_keywords = product_page_soup.find(attrs={"name": "keywords"})

            description = ''

            product, created = Product.objects.get_or_create(
                slug=slugify(product_page_soup.h1.string),
            )

            product.title = product_page_soup.h1.string
            product.h1 = product_page_soup.h1.string
            product.meta_title = product_page_soup.title.string
            product.meta_description = meta_description.get('content') if meta_description else ''
            product.meta_keywords = meta_keywords.get('content') if meta_keywords else ''
            product.description = description
            product.structure = 'standalone'
            product.product_class = product_class
            product.description = u' '.join(map(unicode, product_page_soup.select_one('#tab-description').contents))
            product.save()
            product.categories.add(category)

            try:
                Redirect.objects.create(old_path=product_link[TRUNCATE_LINK:], new_path=product.get_absolute_url(), site=current_site)
            except IntegrityError as e:
                pass
                # print e
                # print 'duplicated'

            price = Decimal(product_page_soup.select_one('.list-unstyled h2').string[1:])

            try:
                StockRecord.objects.get(product=product)
            except ObjectDoesNotExist:
                StockRecord.objects.create(
                    product=product, price_excl_tax=price, price_retail=price, cost_price=price, partner=partner,
                    partner_sku=random.randint(1, 100000000000000)
                )

            image_html = product_page_soup.find('a', 'thumbnail')

            self.save_image(product, image_html)
            images = product_page_soup.select('.thumbnails .image-additional a')

            for image_html in images:
                self.save_image(product, image_html)

        if page:
            try:
                Redirect.objects.create(old_path=relative_path, new_path=category.get_absolute_url(), site=current_site)
            except IntegrityError as e:
                pass
                # print e
                # print 'duplicated'

            categories = category_page_soup.select('#content .col-sm-3 a')

            for category_html in categories:
                category_link = category_html.attrs['href'].encode(encoding='UTF-8', errors='strict')
                self.save_category(category_link, page, category)
        else:
            querydict = QueryDict(relative_path.split('?')[1], mutable=True)
            new_url = '{}?page={}'.format(category.get_absolute_url(), querydict['page'])

            try:
                Redirect.objects.create(
                    old_path=relative_path, new_path=new_url, site=current_site
                )
            except IntegrityError as e:
                pass
                # print e
                # print 'duplicated'
            #
        return category_page_soup

    def save_image(self, product, image_html):
        full_path = os.path.join('media/images/',
                                 os.path.basename(image_html.attrs['href'].encode(encoding='UTF-8', errors='strict')))
        image, httplib = urllib.urlretrieve(image_html.attrs['href'].encode(encoding='UTF-8', errors='strict'),
                                            full_path)

        try:
            image = image.encode(encoding='UTF-8', errors='strict')
        except UnicodeDecodeError:
            pass
            # print image
            # print 'UnicodeDecodeError'
        else:
            filename = os.path.basename(image)
            filepath = image

            user = User.objects.first()
            with open(filepath, "rb") as f:
                file_obj = File(f, name=filename)
                original, created = Image.objects.get_or_create(original_filename=filename)

                if created:
                    original.name = filename
                    original.owner = user
                    original.file = file_obj
                    original.save()
                    # print file_obj

            productimage = ProductImage.objects.filter(product=product).order_by('-display_order')
            display_order = 0

            if productimage.exists():
                display_order = productimage.first().display_order + 1

            try:
                ProductImage.objects.get(product=product, original=original)
            except ObjectDoesNotExist:
                ProductImage.objects.create(product=product, original=original, display_order=display_order)
