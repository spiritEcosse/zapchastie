from django.conf import settings
from import_export import widgets as import_export_widgets
import os
from django.core.exceptions import ObjectDoesNotExist
from filer.models.imagemodels import Image
from django.db import transaction
from oscar.core.loading import get_model
from filer import settings as filer_settings
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

ProductImage = get_model('catalogue', 'ProductImage')


def search_file(image_name, folder):
    """ Given a search path, find file with requested name """
    file = None

    for root, directories, file_names in os.walk(folder):
        for file_name in file_names:
            if file_name == image_name:
                if file is None:
                    file = os.path.join(root, file_name)
                else:
                    raise ValueError('The desired image {} is not unique. Duplicate - {}'.
                                     format(file, os.path.join(root, file_name)))
    return file


class ImageForeignKeyWidget(import_export_widgets.ForeignKeyWidget):
    def clean(self, value):
        if value:
            if not os.path.dirname(value):
                folder = os.path.join(settings.MEDIA_ROOT, filer_settings.DEFAULT_FILER_STORAGES['public']['main']['UPLOAD_TO_PREFIX'])
                image = search_file(value, folder)
                value = '/'.join(os.path.relpath(image).split('/')[1:])

            image = self.model.objects.filter(file=value).first()

            if image is None:
                image = Image.objects.create(**{'file': value, self.field: value})
            return image


class ImageManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def __init__(self, model, separator=None, field=None, *args, **kwargs):
        super(ImageManyToManyWidget, self).__init__(model, separator=separator, field=field, *args, **kwargs)
        self.obj = None

    def clean(self, value):
        product_images = []

        if value:
            images = filter(None, value.split(self.separator))
            upload_to = filer_settings.DEFAULT_FILER_STORAGES['public']['main']['UPLOAD_TO_PREFIX']

            for display_order, val in enumerate(images):
                product_image = ProductImage.objects.filter(
                    product=self.obj, display_order=display_order
                ).first()

                current_path = os.getcwd()
                os.chdir(settings.MEDIA_ROOT)

                if not os.path.dirname(val):
                    folder = os.path.join(settings.MEDIA_ROOT, upload_to)
                    image = search_file(val, folder)

                    if image is not None:
                        val = os.path.relpath(image, start=settings.MEDIA_ROOT)
                else:
                    if not os.path.exists(os.path.abspath(val)):
                        raise ValueError('File "{}" does not exist.'.format(val))

                    if not os.path.isfile(os.path.abspath(val)):
                        raise ValueError('Is not file - "{}" '.format(val))

                os.chdir(current_path)

                image = Image.objects.filter(file=val).first()

                if image is None:
                    image = Image.objects.create(file=val, original_filename=val)

                if product_image is None:
                    product_image = ProductImage.objects.filter(product=self.obj, original__file=val).first()

                    if product_image is None:
                        product_image = ProductImage.objects.create(product=self.obj, original=image, display_order=display_order)
                    else:
                        product_image.display_order = display_order
                        product_image.save()
                    product_images.append(product_image)
                else:
                    product_image.original = image
                    product_image.save()
                    product_images.append(product_image)

            ProductImage.objects.filter(product=self.obj).exclude(pk__in=[obj.pk for obj in product_images]).delete()
        else:
            ProductImage.objects.filter(product=self.obj).delete()
        return product_images


class CharWidget(import_export_widgets.Widget):
    """
    Widget for converting text fields.
    """

    def render(self, value):
        try:
            featured_value = force_text(int(float(value)))
        except ValueError:
            featured_value = force_text(value)
        return featured_value


class ManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def clean(self, value):
        if not value:
            return self.model.objects.none()
        ids = filter(None, value.split(self.separator))
        objects = []

        with transaction.atomic():
            for id in ids:
                try:
                    objects.append(self.model.objects.get(**{self.field: id}))
                except ObjectDoesNotExist as e:
                    raise ValueError('{} {}: \'{}\'.'.format(e, self.model._meta.object_name, id))

        return objects
