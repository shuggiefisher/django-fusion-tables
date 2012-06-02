from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm

class FusionTableExportAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.fields['django_model'].queryset = ContentType.objects.all().exclude(name='fusion table row id')

class FusionTableExportAdmin(ModelAdmin):
    form = FusionTableExportAdminForm
    readonly_fields = ('fusion_table_id', 'fusion_table_url')