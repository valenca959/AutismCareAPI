# autismcare/medical/serializers.py

from rest_framework import serializers
from .models import MedicalRecord, MedicalHistory, Allergy
from patients.models import Child # Importe o modelo Child
from patients.serializers import ChildSerializer
from users.models import AutenticationUser

class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class MedicalRecordSerializer(serializers.ModelSerializer):
    child = ChildSerializer(read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['last_updated', 'created_at']

class MedicalHistorySerializer(serializers.ModelSerializer):
    # Campo para LEITURA (GET): Mostra todos os detalhes da criança.
    child = ChildSerializer(read_only=True)
    
    # Campo para ESCRITA (POST/PUT): Aceita apenas o ID da criança.
    # O 'source='child'' diz ao DRF para usar este valor para preencher o campo 'child' do modelo.
    child_id = serializers.PrimaryKeyRelatedField(
        queryset=Child.objects.all(), source='child', write_only=True
    )
    
    # Este campo é preenchido automaticamente pela view, por isso é apenas de leitura.
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MedicalHistory
        fields = [
            'id',
            'child',        # Usado para ler
            'child_id',     # Usado para escrever
            'date',
            'description',
            'history_type',
            'created_by',
            'created_at',
            'updated_at',
        ]
        # Removemos 'created_by' daqui porque já está definido como read_only acima.
        read_only_fields = ['date', 'created_at', 'updated_at']