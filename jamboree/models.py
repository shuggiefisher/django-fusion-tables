import logging

from django.db import models
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from pyft.fusiontables import FusionTable, DEFAULT_TYPE_HANDLER
from pyft.fields import NumberField, StringField, Row

log = logging.getLogger(__name__)

# docs groups is a model admin which only lets you create groups from a set form

def get_all_models():
    all_models = []
    from django.db.models import get_apps
    for app in get_apps():
        from django.db.models import get_models
        for model in get_models(app):
            new_object = model() # Create a object of type model
            db_table_name = model._meta.db_table # Get the name of the model in the database

            if type(model._meta.verbose_name) is str:
                verbose_name = model._meta.verbose_name
            else:
                verbose_name = db_table_name

            all_models.append((db_table_name, db_table_name))

    return all_models

all_models = get_all_models()

class FusionTableExport(models.Model):
    django_model = models.ForeignKey(ContentType, null=False, blank=False, unique=True, related_name='fusion_table')
    fusion_table_id = models.CharField(null=True, blank=True, max_length=50)
    fusion_table_url = models.URLField(null=False, blank=True, max_length=500)
    read_group = models.ForeignKey(Group, null=True, blank=True)

class FusionTableRowId(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    row_id = models.PositiveIntegerField()

@receiver(pre_save, sender=FusionTableExport)
def add_fusion_table(sender, instance, **kwargs):
    if instance.pk is None:
        fusion_table = create_fusion_table(instance)
        instance.fusion_table_id = fusion_table.table_id
        instance.fusion_table_url = "https://www.google.com/fusiontables/DataSource?dsrcid=%s" %fusion_table.table_id

def create_fusion_table(instance):
    fusion_table_name = "%s - %s" %(instance.django_model.app_label, instance.django_model.name)
    schema = get_schema_from_model(instance.django_model.model_class())
    column_types = get_column_types_from_schema(schema)
    fusion_table = FusionTable.create(column_types, fusion_table_name)

    return fusion_table

DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP = {
    'django.db.models.fields.CharField': StringField
}

def get_schema_from_model(django_model_class):
    fields = django_model_class._meta.fields
    schema = {}
    for field in fields:
        field_type = field.__class__
        if field_type in DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP:
            schema[field.__class__] = DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP[field_type]
        else:
            schema[field.__class__] = StringField

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
            pass #update_row()
    except FusionTableExport.DoesNotExist:
        pass

def insert_rows(table_id, instances):
    fusion_table = FusionTable(table_id)
    rows = []
    for instance in instances:
        fusion_table_fields = build_fields_for_row(instance)
        rows.append(Row(row_id=None, fields=fusion_table_fields))

    row_ids = fusion_table.insert(rows)

    instance_content_type = ContentType.objects.get_for_model(instance)
    for row_id, instance in zip(row_ids, instances):
        fusion_table_row_id = FusionTableRowId(content_type = instance_content_type,
                                               object_id = instance.pk,
                                               row_id = row_id)
        fusion_table_row_id.save()

def update_rows(table_id, instances):
    fusion_table = FusionTable(table_id)
    instance_content_type = ContentType.objects.get_for_model(instance)

    rows = []
    for instance in instances:
        fusion_table_fields = build_fields_for_row(instance)
        try:
            row_id = FusionTableRowId.objects\
                        .get(content_type = instance_content_type, object_id = instance.pk)
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
        fusion_table_fields.append(schema[field.__class__](getattr(instance, field.name), column_name=field.name))
    return fusion_table_fields