from rest_framework import serializers
from .models import AutenticationUser, Address, Role, Employee

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AutenticationUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = AutenticationUser
        fields = [
            'id', 'email', 'username', 'address', 'telephone', 'telephone2',
            'birthdate', 'cpf', 'first_name', 'last_name', 'user_type',
            'date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at',
        ]
        read_only_fields = ['date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at']

    def get_user_type(self, obj):
        return obj.get_user_type()

class RoleSerializer(serializers.ModelSerializer):
    parent_role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True)

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class EmployeeSerializer(serializers.ModelSerializer):
    user = AutenticationUserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']