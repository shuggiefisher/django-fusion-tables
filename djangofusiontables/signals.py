from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from models import FusionTableExport, FusionTableRowId
from fusiontables import create_fusion_table, insert_rows, update_row, delete_row

@receiver(pre_save, sender=FusionTableExport)
def add_fusion_table(sender, instance, **kwargs):
    if instance.pk is None:
        # ought to check that the fusion table models have not been added
        fusion_table = create_fusion_table(instance)
        instance.fusion_table_id = fusion_table.table_id
        instance.fusion_table_url = "https://www.google.com/fusiontables/DataSource?dsrcid=%s" %fusion_table.table_id

@receiver(post_save)
def fusion_model_change(sender, instance, created, **kwargs):
    sender_type = ContentType.objects.get_for_model(sender)
    try:
        sender_fusion_table = sender_type.fusion_table.exclude(fusion_table_id=None).get()
        if created is True:
            insert_rows(sender_fusion_table.fusion_table_id, [instance])
        else:
            update_row(sender_fusion_table.fusion_table_id, instance)
    except FusionTableExport.DoesNotExist:
        pass

@receiver(pre_delete)
def fusion_model_row_delete(sender, instance, **kwargs):
    sender_type = ContentType.objects.get_for_model(sender)
    if sender not in [FusionTableExport, FusionTableRowId]:
        try:
            sender_fusion_table = sender_type.fusion_table.exclude(fusion_table_id=None).get()
            delete_row(sender_fusion_table.fusion_table_id, instance)
        except FusionTableExport.DoesNotExist:
            pass
    elif sender is FusionTableExport:
        # delete all the FusionTableRowIds associated with the sender Model
        FusionTableRowId.objects.filter(content_type = sender_type).delete()