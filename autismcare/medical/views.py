# autismcare/medical/views.py

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from users.permissions import (
    get_employee,
    is_coordenador,
    is_responsavel,
    is_terapeuta,
    terapeuta_pode_registrar,
    IsCoordenador,
    ProfissionalDeSaudeComEdicaoPropria,
    ReadOnlyOrProfissionalDeSaude,
)
from .models import MedicalRecord, MedicalHistory, Allergy, RegistroAcesso
from .serializers import (
    MedicalRecordSerializer,
    MedicalHistorySerializer,
    AllergySerializer,
    RegistroAcessoSerializer,
)

MSG_SEM_ESCOPO = 'Você só pode registrar dados de crianças agendadas com você.'


class RegistroAcessoMixin:
    """Registra leituras de dados médicos (LGPD: quem acessou o quê e quando)."""
    recurso = 'desconhecido'

    def _registrar(self, acao, registro_id=''):
        RegistroAcesso.objects.create(
            usuario=self.request.user,
            recurso=self.recurso,
            acao=acao,
            registro_id=str(registro_id),
        )

    def list(self, request, *args, **kwargs):
        self._registrar('listagem')
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self._registrar('leitura', kwargs.get('pk', ''))
        return super().retrieve(request, *args, **kwargs)


class AllergyViewSet(viewsets.ModelViewSet):
    # Catálogo de alergias: leitura para autenticados, escrita para terapeuta/coordenador.
    queryset = Allergy.objects.order_by('name')
    serializer_class = AllergySerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrProfissionalDeSaude]


class MedicalRecordViewSet(RegistroAcessoMixin, viewsets.ModelViewSet):
    recurso = 'prontuario'
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrProfissionalDeSaude]

    def get_queryset(self):
        user = self.request.user
        qs = MedicalRecord.objects.select_related('child__parent__user').prefetch_related('allergies').order_by('pk')
        if is_coordenador(user):
            return qs.all()
        if is_terapeuta(user):
            return qs.filter(child__agendamentos__terapeuta=get_employee(user)).distinct()
        # Recepção e responsáveis não veem o prontuário.
        return qs.none()

    def perform_create(self, serializer):
        if not terapeuta_pode_registrar(self.request.user, serializer.validated_data['child']):
            raise PermissionDenied(MSG_SEM_ESCOPO)
        serializer.save()

    def perform_update(self, serializer):
        child = serializer.validated_data.get('child', serializer.instance.child)
        if not terapeuta_pode_registrar(self.request.user, child):
            raise PermissionDenied(MSG_SEM_ESCOPO)
        serializer.save()

    def perform_destroy(self, instance):
        if not is_coordenador(self.request.user):
            raise PermissionDenied('Somente o coordenador pode excluir prontuários.')
        instance.delete()


class MedicalHistoryViewSet(RegistroAcessoMixin, viewsets.ModelViewSet):
    recurso = 'anotacao'
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, ProfissionalDeSaudeComEdicaoPropria]

    def get_queryset(self):
        user = self.request.user
        qs = MedicalHistory.objects.select_related('child__parent__user', 'created_by')
        if is_coordenador(user):
            return qs.all()
        if is_terapeuta(user):
            return qs.filter(child__agendamentos__terapeuta=get_employee(user)).distinct()
        if is_responsavel(user):
            # Responsável só acompanha as anotações do próprio filho.
            return qs.filter(child__parent__user=user)
        # Recepção não vê anotações médicas.
        return qs.none()

    def perform_create(self, serializer):
        if not terapeuta_pode_registrar(self.request.user, serializer.validated_data['child']):
            raise PermissionDenied(MSG_SEM_ESCOPO)
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        child = serializer.validated_data.get('child', serializer.instance.child)
        if not terapeuta_pode_registrar(self.request.user, child):
            raise PermissionDenied(MSG_SEM_ESCOPO)
        serializer.save()


class RegistroAcessoViewSet(viewsets.ReadOnlyModelViewSet):
    """Auditoria de acessos: só o coordenador consulta."""
    queryset = RegistroAcesso.objects.select_related('usuario')
    serializer_class = RegistroAcessoSerializer
    permission_classes = [IsAuthenticated, IsCoordenador]
