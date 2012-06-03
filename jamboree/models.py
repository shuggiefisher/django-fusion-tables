from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class FusionTableExport(models.Model):
    django_model = models.ForeignKey(ContentType, null=False, blank=False, unique=True, related_name='fusion_table')
    # this field ought to be immutable

    fusion_table_id = models.PositiveIntegerField(null=True, blank=True, max_length=50)
    fusion_table_url = models.URLField(null=False, blank=True, max_length=500)

    def __unicode__(self):
        return "%s : %s : %s" %(self.django_model, self.read_group, self.fusion_table_id)

class FusionTableRowId(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    row_id = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s : %s : %s" %(self.content_type, self.object_id, self.row_id)

import signals