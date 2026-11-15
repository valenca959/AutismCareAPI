from django.contrib import admin
from .models import Parent, Child, Agendamento


class ChildInline(admin.TabularInline):
    model = Child
    extra = 0
    fields = ('first_name', 'last_name', 'birthdate', 'gender')


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'spouse', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_select_related = ('user',)
    raw_id_fields = ('user',)
    inlines = [ChildInline]


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birthdate', 'gender', 'parent')
    list_filter = ('gender',)
    search_fields = ('first_name', 'last_name', 'parent__user__email')
    list_select_related = ('parent__user',)
    raw_id_fields = ('parent',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'child', 'terapeuta')
    list_filter = ('terapeuta', 'data_hora')
    search_fields = ('child__first_name', 'child__last_name', 'terapeuta__user__email')
    date_hierarchy = 'data_hora'
    list_select_related = ('child__parent__user', 'terapeuta__user', 'terapeuta__role')
    raw_id_fields = ('child', 'terapeuta')
