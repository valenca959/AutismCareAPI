from django.contrib import admin
from .models import Allergy, MedicalRecord, MedicalHistory

admin.site.register(Allergy)
admin.site.register(MedicalRecord)
admin.site.register(MedicalHistory)