from django.contrib import admin
from .models import AutenticationUser, Address, Role, Employee

admin.site.register(AutenticationUser)
admin.site.register(Address)
admin.site.register(Role)
admin.site.register(Employee)