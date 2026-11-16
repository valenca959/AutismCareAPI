from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import (
    get_employee,
    is_recepcao_ou_coordenador,
    is_terapeuta,
    ReadOnlyOrRecepcaoOuCoordenador,
)
from .models import Parent, Child, Agendamento
from .serializers import ParentSerializer, ChildSerializer, AgendamentoSerializer


class ParentViewSet(viewsets.ModelViewSet):
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrRecepcaoOuCoordenador]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # geração do Swagger, sem usuário real
            return Parent.objects.none()
        user = self.request.user
        qs = Parent.objects.select_related('user').prefetch_related('children').order_by('user__first_name', 'pk')
        if is_recepcao_ou_coordenador(user):
            return qs.all()
        if is_terapeuta(user):
            # Responsáveis das crianças agendadas com o terapeuta.
            return qs.filter(children__agendamentos__terapeuta=get_employee(user)).distinct()
        return qs.filter(user=user)


class ChildViewSet(viewsets.ModelViewSet):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrRecepcaoOuCoordenador]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # geração do Swagger, sem usuário real
            return Child.objects.none()
        user = self.request.user
        qs = Child.objects.select_related('parent__user').order_by('first_name', 'last_name', 'pk')
        if is_recepcao_ou_coordenador(user):
            return qs.all()
        if is_terapeuta(user):
            return qs.filter(agendamentos__terapeuta=get_employee(user)).distinct()
        return qs.filter(parent__user=user)


class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrRecepcaoOuCoordenador]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # geração do Swagger, sem usuário real
            return Agendamento.objects.none()
        user = self.request.user
        qs = Agendamento.objects.select_related('child', 'terapeuta__user', 'terapeuta__role')
        if is_recepcao_ou_coordenador(user):
            return qs.all()
        if is_terapeuta(user):
            return qs.filter(terapeuta=get_employee(user))
        # Responsável acompanha (só leitura) os atendimentos dos próprios filhos.
        return qs.filter(child__parent__user=user)
