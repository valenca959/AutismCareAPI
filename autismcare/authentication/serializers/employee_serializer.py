from rest_framework import serializers
from authentication.models.employee import Employee
from .base_serializer import AutenticationUserSerializer
from .role_serializer import RoleSerializer

class EmployeeSerializer(serializers.ModelSerializer):
    user = AutenticationUserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'role',
            'salary',
            'admission_date',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']