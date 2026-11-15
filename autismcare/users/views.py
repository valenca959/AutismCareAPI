from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView

from medical.models import RegistroAcesso
from .models import AuthenticationUser, Address, Role, Employee
from .serializers import (
    AuthenticationUserSerializer,
    AddressSerializer,
    RoleSerializer,
    EmployeeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .emails import enviar_email_senha
from .lgpd import anonimizar_usuario
from .permissions import (
    get_employee,
    is_recepcao_ou_coordenador,
    is_terapeuta,
    IsCoordenador,
    IsSelfOrRecepcaoOuCoordenador,
    ReadOnlyOrRecepcaoOuCoordenador,
)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrRecepcaoOuCoordenador]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):  # geração do Swagger, sem usuário real
            return Address.objects.none()
        user = self.request.user
        if is_recepcao_ou_coordenador(user):
            return Address.objects.order_by('pk')
        return Address.objects.filter(user=user).order_by('pk')


class AuthenticationUserViewSet(viewsets.ModelViewSet):
    serializer_class = AuthenticationUserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrRecepcaoOuCoordenador]

    def get_queryset(self):
        user = self.request.user
        qs = AuthenticationUser.objects.select_related('address').order_by('email')
        if is_recepcao_ou_coordenador(user):
            return qs.all()
        if is_terapeuta(user):
            # Próprio cadastro + responsáveis das crianças agendadas com ele.
            return qs.filter(
                Q(pk=user.pk) | Q(parent__children__agendamentos__terapeuta=get_employee(user))
            ).distinct()
        return qs.filter(pk=user.pk)

    def perform_create(self, serializer):
        user = serializer.save()
        enviar_email_senha(user)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Dados do usuário logado, incluindo o user_type (employee, parent...)."""
        return Response(self.get_serializer(request.user).data)

    def destroy(self, request, *args, **kwargs):
        # Apagar o usuário apagaria o prontuário em cascata. Use a anonimização.
        return Response(
            {'detail': 'Exclusão não permitida. Use /anonimizar/ para remover dados pessoais e manter o prontuário.'},
            status=405,
        )

    @action(detail=True, methods=['post'], url_path='anonimizar',
            permission_classes=[IsAuthenticated, IsCoordenador])
    def anonimizar(self, request, pk=None):
        user = self.get_object()
        anonimizar_usuario(user)
        RegistroAcesso.objects.create(
            usuario=request.user, recurso='usuario', registro_id=str(user.pk), acao='anonimizacao',
        )
        return Response({'detail': 'Dados pessoais removidos e conta desativada.'})


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsCoordenador]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'role').order_by('user__email')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsCoordenador]


_DETAIL = inline_serializer('Detalhe', {'detail': serializers.CharField()})


class LoginView(TokenObtainPairView):
    """Login (JWT) com limite de tentativas por IP, contra ataques de força bruta."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'


class PasswordResetRequestView(APIView):
    """Envia o link de senha. Responde sempre igual, para não revelar quais emails existem."""
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    @extend_schema(request=PasswordResetRequestSerializer, responses={200: _DETAIL})
    def post(self, request):
        email = str(request.data.get('email', '')).strip()
        user = None
        if email:
            user = AuthenticationUser.objects.filter(email__iexact=email, is_active=True).first()
        if user is not None:
            enviar_email_senha(user)
        return Response({'detail': 'Se o email estiver cadastrado, enviaremos o link.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_confirm'

    @extend_schema(request=PasswordResetConfirmSerializer, responses={200: _DETAIL, 400: _DETAIL})
    def post(self, request):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '')
        try:
            user = AuthenticationUser.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        except (TypeError, ValueError, OverflowError, AuthenticationUser.DoesNotExist):
            user = None
        if user is None or not default_token_generator.check_token(user, token):
            return Response({'detail': 'Link inválido ou expirado.'}, status=400)
        try:
            validate_password(new_password, user=user)
        except ValidationError as erro:
            return Response({'new_password': erro.messages}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Senha definida com sucesso.'})
