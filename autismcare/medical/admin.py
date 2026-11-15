from django.contrib import admin
from .models import Allergy, MedicalRecord, MedicalHistory, RegistroAcesso


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('child', 'last_updated')
    search_fields = ('child__first_name', 'child__last_name')
    list_select_related = ('child',)
    raw_id_fields = ('child',)
    filter_horizontal = ('allergies',)


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('child', 'history_type', 'date', 'created_by')
    list_filter = ('history_type', 'date')
    search_fields = ('child__first_name', 'child__last_name')
    date_hierarchy = 'date'
    list_select_related = ('child', 'created_by')
    raw_id_fields = ('child', 'created_by')


@admin.register(RegistroAcesso)
class RegistroAcessoAdmin(admin.ModelAdmin):
    """Trilha de auditoria (LGPD): só leitura, ninguém cria, altera ou apaga pelo admin."""
    list_display = ('criado_em', 'usuario', 'acao', 'recurso', 'registro_id')
    list_filter = ('acao', 'recurso', 'criado_em')
    search_fields = ('usuario__email', 'registro_id')
    date_hierarchy = 'criado_em'
    list_select_related = ('usuario',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
