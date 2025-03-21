from rest_framework import serializers
from authentication.models.medical import MedicalRecord, MedicalHistory, Allergy
from .child_serializer import ChildSerializer
from authentication.models.base import AutenticationUser

class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = [
            'id',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

class MedicalRecordSerializer(serializers.ModelSerializer):
    child = ChildSerializer(read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id',
            'child',
            'allergies',
            'notes',
            'last_updated',
            'created_at',
        ]
        read_only_fields = ['last_updated', 'created_at']

class MedicalHistorySerializer(serializers.ModelSerializer):
    child = ChildSerializer(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(queryset=AutenticationUser.objects.all(), allow_null=True)

    class Meta:
        model = MedicalHistory
        fields = [
            'id',
            'child',
            'date',
            'description',
            'history_type',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['date', 'created_at', 'updated_at']