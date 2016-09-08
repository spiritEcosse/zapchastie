from import_export.resources import ModelResource
from import_export import resources, fields
from diff_match_patch import diff_match_patch
from django.utils.safestring import mark_safe
from import_export.results import RowResult
from copy import deepcopy
from django.db import transaction
from django.db.transaction import TransactionManagementError
import widgets
import traceback
from import_export import widgets as import_export_widgets
from models import Feature
import logging  # isort:skip
from django.utils.encoding import force_text


# class ModelResource(resources.ModelResource):
#     prefix = 'rel_'
#
#     def for_delete(self, row, instance):
#         return self.fields['delete'].clean(row)
#
#     def copy_relation(self, obj):
#         for field in self.get_fields():
#             if isinstance(field.widget, widgets.ImageManyToManyWidget) \
#                     or isinstance(field.widget, widgets.ManyToManyWidget):
#                 setattr(obj, '{}{}'.format(self.prefix, field.column_name), self.export_field(field, obj))
#
#     # def import_row(self, row, instance_loader, dry_run=False, **kwargs):
#     #     """
#     #     Imports data from ``tablib.Dataset``. Refer to :doc:`import_workflow`
#     #     for a more complete description of the whole import process.
#     #
#     #     :param row: A ``dict`` of the row to import
#     #
#     #     :param instance_loader: The instance loader to be used to load the row
#     #
#     #     :param dry_run: If ``dry_run`` is set, or error occurs, transaction
#     #         will be rolled back.
#     #     """
#     #     try:
#     #         row_result = self.get_row_result_class()()
#     #         instance, new = self.get_or_init_instance(instance_loader, row)
#     #         if new:
#     #             row_result.import_type = RowResult.IMPORT_TYPE_NEW
#     #         else:
#     #             row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
#     #         row_result.new_record = new
#     #         row_result.object_repr = force_text(instance)
#     #         row_result.object_id = instance.pk
#     #         original = deepcopy(instance)
#     #         self.copy_relation(original)
#     #
#     #         if self.for_delete(row, instance):
#     #             if new:
#     #                 row_result.import_type = RowResult.IMPORT_TYPE_SKIP
#     #                 row_result.diff = self.get_diff(None, None, dry_run)
#     #             else:
#     #                 row_result.import_type = RowResult.IMPORT_TYPE_DELETE
#     #                 self.delete_instance(instance, dry_run)
#     #                 row_result.diff = self.get_diff(original, None, dry_run)
#     #         else:
#     #             self.import_obj(instance, row, dry_run)
#     #             if self.skip_row(instance, original):
#     #                 row_result.import_type = RowResult.IMPORT_TYPE_SKIP
#     #             else:
#     #                 with transaction.atomic():
#     #                     self.save_instance(instance, dry_run)
#     #                 self.save_m2m(instance, row, dry_run)
#     #                 # Add object info to RowResult for LogEntry
#     #                 row_result.object_repr = force_text(instance)
#     #                 row_result.object_id = instance.pk
#     #             row_result.diff = self.get_diff(original, instance, dry_run)
#     #     except Exception as e:
#     #         # There is no point logging a transaction error for each row
#     #         # when only the original error is likely to be relevant
#     #         if not isinstance(e, TransactionManagementError):
#     #             logging.exception(e)
#     #         tb_info = traceback.format_exc()
#     #         row_result.errors.append(self.get_error_result_class()(e, tb_info, row))
#     #     return row_result
#
#     # def get_diff(self, original, current, dry_run=False):
#     #     """
#     #     Get diff between original and current object when ``import_data``
#     #     is run.
#     #
#     #     ``dry_run`` allows handling special cases when object is not saved
#     #     to database (ie. m2m relationships).
#     #     """
#     #     data = []
#     #     dmp = diff_match_patch()
#     #     for field in self.get_fields():
#     #         attr = '{}{}'.format(self.prefix, field.column_name)
#     #
#     #         if hasattr(original, attr):
#     #             v1 = getattr(original, attr)
#     #         else:
#     #             v1 = self.export_field(field, original) if original else ""
#     #
#     #         v2 = self.export_field(field, current) if current else ""
#     #
#     #         diff = dmp.diff_main(force_text(v1), force_text(v2))
#     #         dmp.diff_cleanupSemantic(diff)
#     #         html = dmp.diff_prettyHtml(diff)
#     #         html = mark_safe(html)
#     #         data.append(html)
#     #     # return data
#
#     def save_m2m(self, obj, data, using_transactions, dry_run):
#         """
#         Saves m2m fields.
#
#         Model instance need to have a primary key value before
#         a many-to-many relationship can be used.
#         """
#         if not dry_run:
#             for field in self.get_fields():
#                 field.widget.obj = obj
#                 if not isinstance(field.widget, widgets.ManyToManyWidget) \
#                         and not isinstance(field.widget, widgets.ImageManyToManyWidget):
#                     continue
#                 self.import_field(field, obj, data)


class FeatureResource(ModelResource):
    title = fields.Field(column_name='title', attribute='title', widget=widgets.CharWidget())
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'enable', 'title', 'slug', 'parent', 'sort',)
        export_order = fields
