from rest_framework import serializers
from .models import MedicalRecord, MedicalHistory, Allergy
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
    child = ChildSerializer(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=AutenticationUser.objects.all(), allow_null=True)

    class Meta:
        model = MedicalHistory
        fields = '__all__'
        read_only_fields = ['date', 'created_at', 'updated_at']