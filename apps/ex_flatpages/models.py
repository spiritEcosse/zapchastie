from fluent_comments.moderation import moderate_model
from django.contrib.flatpages.models import FlatPage
from django.db import models
from django.utils.translation import ugettext_lazy as _


publication_date = models.DateField(verbose_name=_('Publication'), auto_now_add=True)
publication_date.contribute_to_class(FlatPage, 'publication_date')
moderate_model(FlatPage, publication_date_field='publication_date', enable_comments_field='enable_comments')
