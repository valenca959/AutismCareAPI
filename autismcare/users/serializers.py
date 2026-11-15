from rest_framework import serializers
from .models import AuthenticationUser, Address, Role, Employee
from .fields import hash_cpf

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AuthenticationUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = AuthenticationUser
        fields = [
            'id', 'email', 'address', 'telephone', 'telephone2',
            'birthdate', 'cpf', 'first_name', 'last_name', 'user_type',
            'date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at',
        ]
        read_only_fields = ['date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at']

    def get_user_type(self, obj):
        return obj.get_user_type()

    def validate_cpf(self, value):
        qs = AuthenticationUser.objects.filter(cpf_hash=hash_cpf(value))
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Já existe usuário com este CPF.')
        return value

    def create(self, validated_data):
        # Sem senha no cadastro: o usuário define a senha pelo link enviado por email.
        user = AuthenticationUser(**validated_data)
        user.set_unusable_password()
        user.save()
        return user

class RoleSerializer(serializers.ModelSerializer):
    parent_role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True)

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class EmployeeSerializer(serializers.ModelSerializer):
    user = AuthenticationUserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
