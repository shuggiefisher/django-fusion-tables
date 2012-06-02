from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm

from models import FusionTableExport, FusionTableRowId

class FusionTableExportAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FusionTableExportAdminForm, self ).__init__(*args, **kwargs)
        self.fields['django_model'].queryset = ContentType.objects.all()\
                                                    .exclude(name='fusion table row id')\
                                                    .exclude(name='fusion table export')

    class Meta:
        model = FusionTableExport

class FusionTableExportAdmin(admin.ModelAdmin):
    form = FusionTableExportAdminForm
    readonly_fields = ('fusion_table_id', 'fusion_table_url')

admin.site.register(FusionTableExport, FusionTableExportAdmin)
admin.site.register(FusionTableRowId)