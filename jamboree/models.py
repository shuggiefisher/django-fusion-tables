import logging

from django.db import models
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from pyft.fusiontables import FusionTable, DEFAULT_TYPE_HANDLER
from pyft.fields import NumberField, StringField, Row

log = logging.getLogger(__name__)

# docs groups is a model admin which only lets you create groups from a set form

class FusionTableExport(models.Model):
    django_model = models.ForeignKey(ContentType, null=False, blank=False, unique=True, related_name='fusion_table')
    fusion_table_id = models.PositiveIntegerField(null=True, blank=True, max_length=50)
    fusion_table_url = models.URLField(null=False, blank=True, max_length=500)
    read_group = models.ForeignKey(Group, null=True, blank=True)

    def __unicode__(self):
        return "%s : %s : %s" %(self.django_model, self.read_group, self.fusion_table_id)

class FusionTableRowId(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    row_id = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s : %s : %s" %(self.content_type, self.object_id, self.row_id)

@receiver(pre_save, sender=FusionTableExport)
def add_fusion_table(sender, instance, **kwargs):
    if instance.pk is None:
        # ought to check that the fusion table models have not been added
        fusion_table = create_fusion_table(instance)
        instance.fusion_table_id = fusion_table.table_id
        instance.fusion_table_url = "https://www.google.com/fusiontables/DataSource?dsrcid=%s" %fusion_table.table_id

def create_fusion_table(instance):
    fusion_table_name = "%s - %s" %(instance.django_model.app_label, instance.django_model.name)
    schema = get_schema_from_model(instance.django_model.model_class())
    column_types = get_column_types_from_schema(schema)
    fusion_table = FusionTable.create(column_types, fusion_table_name)

    initialise_fusion_table(fusion_table, instance.django_model.model_class())

    return fusion_table

def initialise_fusion_table(fusion_table, django_model_class):
    # this could be slow, probably should be implmented as a custom serializer
    insert_rows(fusion_table.table_id, list(django_model_class.objects.all()), fusion_table)


DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP = {
    'django.db.models.fields.CharField': StringField
}

def get_schema_from_model(django_model_class):
    fields = django_model_class._meta.fields
    schema = {}
    for field in fields:
        field_type = field.__class__
        if field_type in DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP:
            schema[field.name] = DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP[field_type]
        else:
            schema[field.name] = StringField

    return schema

def get_column_types_from_schema(schema):
    column_types = {}
    for key in schema:
        column_types[key] = schema[key].column_type
    return column_types

@receiver(post_save)
def fusion_model_change(sender, instance, created, **kwargs):
    sender_type = ContentType.objects.get_for_model(sender)
    try:
        sender_fusion_table = sender_type.fusion_table.exclude(fusion_table_id=None).get()
        if created is True:
            insert_rows(sender_fusion_table.fusion_table_id, [instance])
        else:
            update_rows(sender_fusion_table.fusion_table_id, [instance])
    except FusionTableExport.DoesNotExist:
        pass

@receiver(post_delete)
def fusion_model_row_delete(sender, instance, **kwargs):
    if sender not in [FusionTableExport, FusionTableRowId]:
        sender_type = ContentType.objects.get_for_model(sender)
        try:
            sender_fusion_table = sender_type.fusion_table.exclude(fusion_table_id=None).get()
            #delete_rows(sender_fusion_table.table_id, [instance])
        except FusionTableExport.DoesNotExist:
            pass


def insert_rows(table_id, instances, fusion_table=None):
    if fusion_table is None:
        fusion_table = FusionTable(table_id)
    rows = []
    for instance in instances:
        fusion_table_fields = build_fields_for_row(instance)
        rows.append(Row(row_id=None, fields=fusion_table_fields))

    row_ids = fusion_table.insert(rows)

    instance_content_type = ContentType.objects.get_for_model(instances[0])
    for row_id, instance in zip(row_ids, instances):
        fusion_table_row_id = FusionTableRowId(content_type = instance_content_type,
                                               object_id = instance.pk,
                                               row_id = row_id)
        fusion_table_row_id.save()

def update_rows(table_id, instances):
    fusion_table = FusionTable(table_id)
    instance_content_type = ContentType.objects.get_for_model(instances[0])

    rows = []
    for instance in instances:
        fusion_table_fields = build_fields_for_row(instance)
        try:
            row_id = FusionTableRowId.objects\
                        .get(content_type = instance_content_type, object_id = instance.pk).row_id
            rows.append(Row(row_id=row_id, fields=fusion_table_fields))
        except FusionTableRowId.DoesNotExist:
            log.error('Could not find the fusion table row id for existing %s instance pk : %s'
                            %(instance_content_type, instance.pk))

    fusion_table.update(rows)

def build_fields_for_row(instance):
    django_model = instance.__class__
    fields = django_model._meta.fields
    schema = get_schema_from_model(django_model)
    fusion_table_fields = []
    for field in fields:
        # create a field using the Django->FusionTable map and set it's value
        fusion_table_fields.append(schema[field.name](getattr(instance, field.name), column_name=field.name))
    return fusion_table_fields