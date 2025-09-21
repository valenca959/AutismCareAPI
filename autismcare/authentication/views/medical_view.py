from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from authentication.models.medical import MedicalRecord, MedicalHistory, Allergy
from authentication.serializers.medical_serializer import (
    MedicalRecordSerializer,
    MedicalHistorySerializer,
    AllergySerializer,
)
from authentication.permissions import IsEmployeeOrReadOnly

class AllergyViewSet(viewsets.ModelViewSet):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, IsEmployeeOrReadOnly]

class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.select_related('child__parent__user').prefetch_related('allergies')
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated, IsEmployeeOrReadOnly]

class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.select_related('child__parent__user', 'created_by')
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, IsEmployeeOrReadOnly]