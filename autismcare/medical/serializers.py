from rest_framework import serializers
from .models import MedicalRecord, MedicalHistory, Allergy, RegistroAcesso
from patients.models import Child
from patients.serializers import ChildSerializer


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    # Escrita: id da criança. Leitura: dados da criança em child_detail.
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    child_detail = ChildSerializer(source='child', read_only=True)
    allergies = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Allergy.objects.all(), required=False
    )

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['last_updated', 'created_at']


class MedicalHistorySerializer(serializers.ModelSerializer):
    # Escrita: id da criança. Leitura: dados da criança em child_detail.
    # created_by não vem do cliente: é preenchido com o usuário logado na view.
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    child_detail = ChildSerializer(source='child', read_only=True)

    class Meta:
        model = MedicalHistory
        fields = '__all__'
        read_only_fields = ['date', 'created_by', 'created_at', 'updated_at']


class RegistroAcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroAcesso
        fields = '__all__'
        read_only_fields = ['criado_em']
