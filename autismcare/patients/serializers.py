from rest_framework import serializers
from .models import Parent, Child, Agendamento
from users.models import AuthenticationUser
from users.serializers import AuthenticationUserSerializer

class ChildSerializer(serializers.ModelSerializer):
    # Escrita: recebe o id do Parent. Leitura: dados do usuário responsável.
    parent = serializers.PrimaryKeyRelatedField(queryset=Parent.objects.all())
    parent_detail = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_parent_detail(self, obj):
        return AuthenticationUserSerializer(obj.parent.user).data

class ParentSerializer(serializers.ModelSerializer):
    # Leitura: dados do usuário em `user`. Escrita: id do usuário em `user_id`.
    user = AuthenticationUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source='user', queryset=AuthenticationUser.objects.all(), write_only=True
    )
    children = ChildSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_user_id(self, user):
        if hasattr(user, 'employee'):
            raise serializers.ValidationError('Um funcionário não pode ser cadastrado como responsável.')
        outro = Parent.objects.filter(user=user)
        if self.instance is not None:
            outro = outro.exclude(pk=self.instance.pk)
        if outro.exists():
            raise serializers.ValidationError('Este usuário já é um responsável.')
        return user

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'
        read_only_fields = ['created_at']
