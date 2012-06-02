from django.db import models
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from django.db.models.signals import pre_save
from django.dispatch import receiver

from pyft.fusiontables import FusionTable, DEFAULT_TYPE_HANDLER
from pyft.fields import NumberField
from pyft.fields import StringField

# Create your models here.

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

class FusionTablesExports(models.Model):
    django_model = models.ForeignKey(ContentType, null=False, blank=False, editable=False)
    fusion_table_id = models.CharField(null=True, blank=False, max_length=50, editable=False)
    fusion_table_url = models.URLField(null=False, blank=False, max_length=500, editable=False)
    read_group = models.ForeignKey(Group, null=True, blank=True)

@receiver(pre_save, sender=FusionTablesExports)
def add_fusion_table(sender, instance, **kwargs):
    if not instance._entity_exists:
        fusion_table = create_fusion_table(instance)
        instance.fusion_table_id = fusion_table.table_id
        instance.fusion_table_url = "https://www.google.com/fusiontables/DataSource?docid=" + fusion_table.table_id

def create_fusion_table(instance):
    fusion_table_name = "%s - %s" %(instance.django_model.app_label, instance.django_model.name)
    schema = get_schema_from_model(instance.django_model)
    fusion_table = FusionTable.create(schema, fusion_table_name)

    return fusion_table

DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP = {
    [django.db.models.fields.CharField]: StringField.column_type
}

def get_schema_from_model(django_model):
    django_model_class = django_model.model_class()
    field_names = django_model_class._meta.get_all_field_names()
    schema = {}
    for field_name in field_names:
        field_type = django_model_class._meta.get_field_by_name('id')[0].__class__
        if field_type in DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP:
            schema[field_name] = DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP[field_type]
        else:
            schema[field_name] = StringField.column_type

    return schema