from django.contrib import admin
from .models import Role, Employee

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'salary', 'admission_date')
    list_filter = ('role',)
    search_fields = ('user__username', 'role__name')