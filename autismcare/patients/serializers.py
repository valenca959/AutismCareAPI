from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Parent, Child, Agendamento
from users.models import AuthenticationUser
from users.permissions import ROLE_TERAPEUTA
from users.serializers import AuthenticationUserSerializer

class ChildSerializer(serializers.ModelSerializer):
    # Escrita: recebe o id do Parent. Leitura: dados do usuário responsável.
    parent = serializers.PrimaryKeyRelatedField(queryset=Parent.objects.all())
    parent_detail = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    @extend_schema_field(AuthenticationUserSerializer)
    def get_parent_detail(self, obj):
        # Repassa o contexto (request) para a regra de máscara do CPF.
        return AuthenticationUserSerializer(obj.parent.user, context=self.context).data

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
    crianca_nome = serializers.SerializerMethodField()
    terapeuta_nome = serializers.SerializerMethodField()
    fim = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Agendamento
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_crianca_nome(self, obj) -> str:
        return f'{obj.child.first_name} {obj.child.last_name}'

    def get_terapeuta_nome(self, obj) -> str:
        return obj.terapeuta.user.get_full_name() or obj.terapeuta.user.email

    def validate_terapeuta(self, terapeuta):
        if terapeuta.status != 'active':
            raise serializers.ValidationError('Este funcionário não está ativo.')
        if terapeuta.role is None or terapeuta.role.name.lower() != ROLE_TERAPEUTA:
            raise serializers.ValidationError('Este funcionário não é terapeuta.')
        return terapeuta

    def validate(self, attrs):
        inst = self.instance
        child = attrs.get('child', inst.child if inst else None)
        terapeuta = attrs.get('terapeuta', inst.terapeuta if inst else None)
        inicio = attrs.get('data_hora', inst.data_hora if inst else None)
        duracao = attrs.get('duracao_minutos', inst.duracao_minutos if inst else 60)
        fim = inicio + timedelta(minutes=duracao)

        # Só exige data futura quando o horário é definido ou alterado.
        if 'data_hora' in attrs and (inst is None or attrs['data_hora'] != inst.data_hora):
            if inicio < timezone.now():
                raise serializers.ValidationError({'data_hora': 'Não é possível agendar no passado.'})

        # Candidatos: começam antes do fim deste e no máximo 4 h (duração máxima) antes do início.
        candidatos = Agendamento.objects.filter(
            data_hora__lt=fim, data_hora__gt=inicio - timedelta(minutes=240),
        )
        if inst is not None:
            candidatos = candidatos.exclude(pk=inst.pk)
        conflitos = [a for a in candidatos.filter(terapeuta=terapeuta) if a.fim > inicio]
        if conflitos:
            raise serializers.ValidationError(
                {'data_hora': f'O terapeuta já tem atendimento às {timezone.localtime(conflitos[0].data_hora):%H:%M} neste horário.'}
            )
        conflitos = [a for a in candidatos.filter(child=child) if a.fim > inicio]
        if conflitos:
            raise serializers.ValidationError(
                {'data_hora': f'A criança já tem atendimento às {timezone.localtime(conflitos[0].data_hora):%H:%M} neste horário.'}
            )
        return attrs
