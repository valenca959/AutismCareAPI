from rest_framework import serializers
from .models import Parent, Child, Agendamento
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
    user = AuthenticationUserSerializer(read_only=True)
    children = ChildSerializer(many=True, read_only=True)

    class Meta:
        model = Parent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'
        read_only_fields = ['created_at']
