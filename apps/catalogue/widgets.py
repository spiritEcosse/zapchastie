from django.conf import settings
from import_export import widgets as import_export_widgets
import os
from filer.models.imagemodels import Image
from oscar.core.loading import get_model
from filer import settings as filer_settings
from django.utils.encoding import force_text

ProductImage = get_model('catalogue', 'ProductImage')


class ForeignKeyWidget(import_export_widgets.ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        return super(ForeignKeyWidget, self).clean(value.strip(), row=row, *args, **kwargs)


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


class CharWidget(import_export_widgets.CharWidget):
    """
    Widget for converting text fields.
    """
    def clean(self, value, row=None, *args, **kwargs):
        return super(CharWidget, self).clean(value.strip(), row=row, *args, **kwargs)

    def render(self, value, obj=None):
        try:
            featured_value = int(float(value))
        except ValueError:
            featured_value = value
        return force_text(featured_value)


class ManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()

        ids = filter(None, value.split(self.separator))
        ids = map(lambda slug: slug.strip(), ids)
        return self.model.objects.filter(**{
            '%s__in' % self.field: ids
        })
