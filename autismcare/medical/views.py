# autismcare/medical/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MedicalRecord, MedicalHistory, Allergy
from .serializers import MedicalRecordSerializer, MedicalHistorySerializer, AllergySerializer
from users.permissions import IsEmployeeOrReadOnly

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

    # ADICIONE ESTE MÉTODO
    def perform_create(self, serializer):
        """
        Associa o utilizador logado ao campo 'created_by' ao criar um novo registo.
        """
        serializer.save(created_by=self.request.user)