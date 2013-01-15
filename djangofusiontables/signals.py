from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from urllib2 import URLError

from models import FusionTableExport, FusionTableRowId

@receiver(pre_save, sender=FusionTableExport)
def add_fusion_table(sender, instance, **kwargs):
    # imports happen here because otherwise the client is authorised on import
    # this isn't very helpful because the authorisation to fail whwn offline
    # which will in turn prevent the signals from being registered when offline
    from fusiontables import create_fusion_table

    if instance.pk is None:
        # ought to check that the fusion table models have not been added
        try:
            fusion_table = create_fusion_table(instance)
        except URLError:
            logging.warning("Creating fusion table failed.  Perhaps you are offline?")
        instance.fusion_table_id = fusion_table.table_id
        instance.fusion_table_url = "https://www.google.com/fusiontables/data?docid=%s" %fusion_table.table_id

@receiver(post_save)
def fusion_model_change(sender, instance, created, **kwargs):
    from fusiontables import insert_rows, update_row
    sender_type = ContentType.objects.get_for_model(sender)
    try:
        sender_fusion_table = sender_type.fusion_table.exclude(fusion_table_id=None).get()
    except FusionTableExport.DoesNotExist:
        pass
    else:
        try:
            if created is True:
                insert_rows(sender_fusion_table.fusion_table_id, [instance])
            else:
                update_row(sender_fusion_table.fusion_table_id, instance)
        except URLError:
            logging.warning("Syncing rows to fusion table failed.  Perhaps you are offline?")


@receiver(pre_delete)
def fusion_model_row_delete(sender, instance, **kwargs):
    from fusiontables import delete_row
    sender_type = ContentType.objects.get_for_model(sender)
    if sender not in [FusionTableExport, FusionTableRowId]:
        try:
            sender_fusion_table = sender_type.fusion_table.exclude(fusion_table_id=None).get()
        except FusionTableExport.DoesNotExist:
            pass
        else:
            try:
                delete_row(sender_fusion_table.fusion_table_id, instance)
            except URLError:
                logging.warning("Deleting row from fusion table failed.  Perhaps you are offline?")
    elif sender is FusionTableExport:
        # delete all the FusionTableRowIds associated with the sender Model
        FusionTableRowId.objects.filter(content_type = sender_type).delete()