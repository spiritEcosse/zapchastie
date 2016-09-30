from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
import urllib2, urllib
from bs4 import BeautifulSoup
from apps.catalogue.models import Category, Product, ProductImage, Feature, ProductClass
from oscar.apps.partner.models import StockRecord, Partner
import os
from django.contrib.auth.models import User
from django.core.files import File
from filer.models import Image
from decimal import Decimal
import random
from django.db.utils import IntegrityError
from oscar.core.utils import slugify

timeout = 30

current_site = Site.objects.get(pk=1)
TRUNCATE_LINK = 24
product_class = ProductClass.objects.get(pk=3)
partner = Partner.objects.get(pk=3)


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        Redirect.objects.all().delete()
        Feature.objects.all().delete()
        Image.objects.all().delete()
        Category.objects.all().delete()
        StockRecord.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()

        url = 'http://zapchastie.com.ua/'
        request = urllib2.Request(url)
        request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
        main_page = urllib2.urlopen(request, timeout=timeout)
        soup_main_page = BeautifulSoup(main_page.read(), 'html5lib')
        categories = soup_main_page.select('#menu .navbar-ex1-collapse .navbar-nav > li > a')

        for category_html in categories:
            category_link = category_html.attrs['href'].encode(encoding='UTF-8', errors='strict')
            self.save_category(category_link)

        self.stdout.write('Successfully write redirects.')

    def save_category(self, category_link, parent_category=None):
        relative_path = category_link[TRUNCATE_LINK:]
        print 'category =================='
        print relative_path, '\n'

        request = urllib2.Request(category_link)
        request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
        category_page = urllib2.urlopen(request, timeout=timeout)
        category_page_soup = BeautifulSoup(category_page.read(), 'html5lib')
        meta_description = category_page_soup.find(attrs={"name": "description"})
        meta_keywords = category_page_soup.find(attrs={"name": "keywords"})

        try:
            category = Category.objects.create(
                name=category_page_soup.h1.string,
                meta_title=category_page_soup.title.string,
                h1=category_page_soup.h1.string,
                meta_description=meta_description.get('content') if meta_description else '',
                meta_keywords=meta_keywords.get('content') if meta_keywords else '',
                description=' '.join(map(str, category_page_soup.find('div', 'col-sm-10').contents)),
                parent=parent_category,
            )
        except IntegrityError as e:
            print e
            print 'duplicated'
        else:
            Redirect.objects.create(old_path=relative_path, new_path=category.get_absolute_url(), site=current_site)

            products = category_page_soup.select('#content .product-thumb > .image > a')

            print 'Products ========================'
            for product_html in products:
                product_link = product_html.attrs['href'].encode(encoding='UTF-8', errors='strict')
                print product_link

                request = urllib2.Request(product_link)
                request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
                product_page = urllib2.urlopen(request, timeout=timeout)
                product_page_soup = BeautifulSoup(product_page.read(), 'html5lib')
                meta_description = product_page_soup.find(attrs={"name": "description"})
                meta_keywords = product_page_soup.find(attrs={"name": "keywords"})

                try:
                    description = ''

                    product = Product.objects.create(
                        title=product_page_soup.h1.string,
                        h1=product_page_soup.h1.string,
                        meta_title=product_page_soup.title.string,
                        meta_description=meta_description.get('content') if meta_description else '',
                        meta_keywords=meta_keywords.get('content') if meta_keywords else '',
                        description=description,
                        structure='standalone',
                        product_class=product_class
                    )
                except IntegrityError as e:
                    print e
                    print 'duplicated'
                else:
                    if product_link != 'http://zapchastie.com.ua/Razborka-Citroen-Berlingo/Generator_1_6_HDI_Citroen_Berlingo' and product_link != 'http://zapchastie.com.ua/Razborka-Folksvagen-LT/Dvigatel-Folksvagen-Lt-2-5-tdi-AHD' and product_link != 'http://zapchastie.com.ua/dvigateli_bu/dvigatel-Pezho-Bokser-2.8jtd' and product_link != 'http://zapchastie.com.ua/dvigateli_bu/Dvigatel-1-4b -Citroen-Berlingo-1' and product_link != 'http://zapchastie.com.ua/dvigateli_bu/Dvigatel-Folksvagen-Lt-2-5-tdi-AHD' and product_link != 'http://zapchastie.com.ua/dvigateli_bu/dvigateli_bu_Peugeot/dvigatel-Pezho-Bokser-2.8jtd' and product_link != 'http://zapchastie.com.ua/dvigateli_bu/dvigateli_bu_Volkswagen/Dvigatel-Folksvagen-Lt-2-5-tdi-AHD':
                        product.description = ' '.join(map(str, product_page_soup.select_one('#tab-description').contents))
                        product.save()

                    product.categories.add(category)
                    Redirect.objects.create(old_path=product_link, new_path=product.get_absolute_url(), site=current_site)

                    price = Decimal(product_page_soup.select_one('.list-unstyled h2').string[1:])
                    StockRecord.objects.get_or_create(product=product, price_excl_tax=price, price_retail=price, cost_price=price, partner=partner, partner_sku=random.randint(1, 100000000000000))
                    image_html = product_page_soup.find('a', 'thumbnail')
                    full_path = os.path.join('media/images/', os.path.basename(image_html.attrs['href'].encode(encoding='UTF-8', errors='strict')))
                    image, httplib = urllib.urlretrieve(image_html.attrs['href'].encode(encoding='UTF-8', errors='strict'), full_path)

                    try:
                        image = image.encode(encoding='UTF-8', errors='strict')
                    except UnicodeDecodeError:
                        pass
                    else:
                        filename = os.path.basename(image)
                        filepath = image

                        user = User.objects.first()
                        with open(filepath, "rb") as f:
                            file_obj = File(f, name=filename)
                            original, created = Image.objects.get_or_create(owner=user, original_filename=filename,
                                                                            file=file_obj)

                        productimage = ProductImage.objects.filter(product=product).order_by('-display_order')
                        display_order = 0

                        if productimage.exists():
                            display_order = productimage.first().display_order + 1

                        ProductImage.objects.get_or_create(product=product, original=original, display_order=display_order)

            categories = category_page_soup.select('#content .col-sm-3 a')

            for category_html in categories:
                category_link = category_html.attrs['href'].encode(encoding='UTF-8', errors='strict')
                self.save_category(category_link, category)
