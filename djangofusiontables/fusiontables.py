import logging

from pyft.fusiontables import FusionTable, DEFAULT_TYPE_HANDLER
from pyft.fields import NumberField, StringField, Row
from pyft.client.sql.sqlbuilder import SQL

from django.contrib.contenttypes.models import ContentType

from models import FusionTableRowId

log = logging.getLogger(__name__)

DJANGO_TO_FUSION_TABLES_FIELD_TYPE_MAP = {
    'django.db.models.fields.CharField': StringField
}

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


def insert_rows(table_id, instances, fusion_table=None):
    """
    Insert rows in a batch
    """
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

def update_row(table_id, instance):
    """
    This generates on query per updated row
    """
    fusion_table = FusionTable(table_id)
    instance_content_type = ContentType.objects.get_for_model(instance)

    rows = []
    row_id = get_fusion_table_row_id_for_instance(instance_content_type, instance)
    if row_id is not None:
        fusion_table_fields = build_fields_for_row(instance)
        rows.append(Row(row_id=row_id, fields=fusion_table_fields))

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

def get_fusion_table_row_id_for_instance(content_type, instance):
    try:
        row_id = FusionTableRowId.objects\
                    .get(content_type = content_type, object_id = instance.pk).row_id
        return row_id
    except FusionTableRowId.DoesNotExist:
        log.error('Could not find the fusion table row id for existing %s instance pk : %s'
                        %(content_type, instance.pk))
        return None

def delete_row(table_id, instance):
    """
    This creates one query per delete so could potentially be very slow.
    If you need to delete rows in batches it would be better to add a method
    to the pyft library following the pattern for insert() batches
    """
    fusion_table = FusionTable(table_id)
    table_content_type = ContentType.objects.get_for_model(instance)

    row_id = get_fusion_table_row_id_for_instance(table_content_type, instance)
    if row_id is not None:
        query = SQL().delete(table_id, row_id)
        fusion_table.run_query(query)
        FusionTableRowId.objects\
                .get(content_type = table_content_type, object_id = instance.pk)\
                .delete()