from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


from djangofusiontables.managers import NaturalKeyManager

models.options.DEFAULT_NAMES = models.options.DEFAULT_NAMES + ('natural_key_field_names',)

class NaturalKeyModel(models.Model):
    """
    Done as a model because class-level attributes like objects cannot be set by mixin
    """
    objects = NaturalKeyManager()

    def natural_key(self):
        return tuple([getattr(self, field_name) for field_name in self._meta.natural_key_field_names])

    class Meta:
        abstract = True


class FusionTableExport(NaturalKeyModel):
    django_model = models.ForeignKey(ContentType, null=False, blank=False, unique=True, related_name='fusion_table')
    # this field ought to be immutable

    fusion_table_id = models.CharField(null=True, blank=True, max_length=50)
    fusion_table_url = models.URLField(null=False, blank=True, max_length=500)

    def __unicode__(self):
        return "%s : %s" %(self.django_model, self.fusion_table_id)

    class Meta:
        natural_key_field_names = ('django_model',)

class FusionTableRowId(NaturalKeyModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    row_id = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s : %s : %s" %(self.content_type, self.object_id, self.row_id)

    class Meta:
        unique_together = (('content_type', 'object_id', 'row_id',),)
        natural_key_field_names = ('django_model',)

import signals