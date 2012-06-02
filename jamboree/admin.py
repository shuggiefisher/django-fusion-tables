from django.contrib import admin
from models import FusionTableExport, FusionTableRowId
from django import forms

class FusionTableExportAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.fields['django_model'].choices = ContentType.objects.all().exclude(name='fusion table row id')

class FusionTableExportAdmin(admin.ModelAdmin):
    form = FusionTableExportAdminForm
    readonly_fields = ('fusion_table_id', 'fusion_table_url')

admin.site.register(FusionTableExport, FusionTableExportAdmin)