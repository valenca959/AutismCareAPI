from ..models.parent import Parent, Child, MedicalRecord, MedicalHistory

from rest_framework import serializers


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__' 

class ChildSerializer(serializers.ModelSerializer):
    parent = serializers.StringRelatedField() 

    class Meta:
        model = Child
        fields = '__all__'


class MedicalRecordSerializer(serializers.ModelSerializer):
    child = serializers.StringRelatedField()

    class Meta:
        model = MedicalRecord
        fields = '__all__'


class MedicalHistorySerializer(serializers.ModelSerializer):
    child = serializers.StringRelatedField()
    history_type = serializers.CharField(source='get_history_type_display') 

    class Meta:
        model = MedicalHistory
        fields = '__all__' 