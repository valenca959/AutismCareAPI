from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .fields import hash_cpf
from .models import AuthenticationUser, Address, Role, Employee


class _CpfUnicoMixin:
    """O CPF fica criptografado, então a unicidade é checada pelo hash."""

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            qs = AuthenticationUser.objects.filter(cpf_hash=hash_cpf(cpf))
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe usuário com este CPF.')
        return cpf


class AuthenticationUserCreationForm(_CpfUnicoMixin, AdminUserCreationForm):
    class Meta:
        model = AuthenticationUser
        fields = ('email', 'cpf', 'telephone')
        field_classes = {}


class AuthenticationUserChangeForm(_CpfUnicoMixin, UserChangeForm):
    class Meta:
        model = AuthenticationUser
        fields = '__all__'
        field_classes = {}


@admin.register(AuthenticationUser)
class AuthenticationUserAdmin(UserAdmin):
    # Formulários do UserAdmin: a senha é gravada com hash, nunca em texto puro.
    form = AuthenticationUserChangeForm
    add_form = AuthenticationUserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {
            'fields': ('first_name', 'last_name', 'cpf', 'birthdate', 'telephone', 'telephone2', 'address'),
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'cpf', 'telephone', 'usable_password', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'number', 'city', 'state', 'zip_code')
    list_filter = ('state',)
    search_fields = ('street', 'city', 'zip_code')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_role')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'admission_date')
    list_filter = ('status', 'role')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_select_related = ('user', 'role')
    raw_id_fields = ('user',)
