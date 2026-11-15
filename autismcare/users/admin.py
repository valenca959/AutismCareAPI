from django.contrib import admin
from .models import AuthenticationUser, Address, Role, Employee

admin.site.register(AuthenticationUser)
admin.site.register(Address)
admin.site.register(Role)
admin.site.register(Employee)