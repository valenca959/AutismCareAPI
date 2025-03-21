from rest_framework import viewsets
from authentication.models.medical import MedicalRecord, MedicalHistory, Allergy
from authentication.serializers.medical_serializer import (
    MedicalRecordSerializer,
    MedicalHistorySerializer,
    AllergySerializer,
)

class AllergyViewSet(viewsets.ModelViewSet):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer

class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer