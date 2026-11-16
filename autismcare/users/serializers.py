from rest_framework import serializers
from .models import AuthenticationUser, Address, Role, Employee
from django.core.exceptions import ValidationError as DjangoValidationError

from .cpf import mascarar_cpf, normalizar_cpf, validar_cpf
from .fields import hash_cpf
from .permissions import is_recepcao_ou_coordenador

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AuthenticationUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()
    # Aceita '123.456.789-09' ou '12345678909'. Na resposta, só o próprio usuário,
    # a recepção e o coordenador veem o CPF completo; os demais veem '***.***.***-09'.
    cpf = serializers.CharField(max_length=14)

    class Meta:
        model = AuthenticationUser
        fields = [
            'id', 'email', 'address', 'telephone', 'telephone2',
            'birthdate', 'cpf', 'first_name', 'last_name', 'user_type',
            'date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at',
        ]
        read_only_fields = ['date_joined', 'is_active', 'is_staff', 'created_at', 'updated_at']

    def get_user_type(self, obj) -> str:
        return obj.get_user_type()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self._pode_ver_cpf_completo(instance):
            data['cpf'] = mascarar_cpf(instance.cpf)
        return data

    def _pode_ver_cpf_completo(self, instance):
        request = self.context.get('request')
        if request is None:  # sem contexto, mostra o mínimo
            return False
        return request.user.pk == instance.pk or is_recepcao_ou_coordenador(request.user)

    def validate_cpf(self, value):
        value = normalizar_cpf(value)
        try:
            validar_cpf(value)
        except DjangoValidationError as erro:
            raise serializers.ValidationError(erro.messages)
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

class PasswordResetRequestSerializer(serializers.Serializer):
    """Email da conta que vai receber o link para definir a senha."""
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """uid e token do link recebido por email, mais a nova senha."""
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)


class RoleSerializer(serializers.ModelSerializer):
    parent_role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), allow_null=True)

    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class EmployeeSerializer(serializers.ModelSerializer):
    # Leitura: objetos completos em `user` e `role`. Escrita: ids em `user_id` e `role_id`.
    user = AuthenticationUserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=AuthenticationUser.objects.all(), write_only=True
    )
    role_id = serializers.PrimaryKeyRelatedField(
        source='role', queryset=Role.objects.all(), write_only=True,
        required=False, allow_null=True,
    )

    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_user_id(self, user):
        if hasattr(user, 'parent'):
            raise serializers.ValidationError('Um responsável não pode ser cadastrado como funcionário.')
        outro = Employee.objects.filter(user=user)
        if self.instance is not None:
            outro = outro.exclude(pk=self.instance.pk)
        if outro.exists():
            raise serializers.ValidationError('Este usuário já é um funcionário.')
        return user
