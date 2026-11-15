from rest_framework import permissions

from patients.models import Agendamento

# Nomes de cargo (Role.name), em minúsculas.
ROLE_RECEPCIONISTA = 'recepcionista'
ROLE_TERAPEUTA = 'terapeuta'
ROLES_COORDENADOR = ('coordenador', 'gerente')

SAFE = permissions.SAFE_METHODS


def get_employee(user):
    """Retorna o Employee ativo do usuário, ou None."""
    if not user or not user.is_authenticated:
        return None
    employee = getattr(user, 'employee', None)
    if employee is None or employee.status != 'active':
        return None
    return employee


def get_role_name(user):
    employee = get_employee(user)
    if employee is None or employee.role is None:
        return None
    return employee.role.name.lower()


def is_coordenador(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or get_role_name(user) in ROLES_COORDENADOR


def is_recepcionista(user):
    return get_role_name(user) == ROLE_RECEPCIONISTA


def is_terapeuta(user):
    return get_role_name(user) == ROLE_TERAPEUTA


def is_recepcao_ou_coordenador(user):
    return is_recepcionista(user) or is_coordenador(user)


def is_responsavel(user):
    return bool(user and user.is_authenticated and hasattr(user, 'parent'))


def terapeuta_pode_registrar(user, child):
    """Coordenador registra em qualquer criança; terapeuta só nas que estão agendadas com ele."""
    if is_coordenador(user):
        return True
    if is_terapeuta(user):
        return Agendamento.objects.filter(child=child, terapeuta=get_employee(user)).exists()
    return False


class ReadOnlyOrRecepcaoOuCoordenador(permissions.BasePermission):
    """Leitura conforme o get_queryset da view; escrita só para recepção e coordenador."""

    def has_permission(self, request, view):
        if request.method in SAFE:
            return True
        return is_recepcao_ou_coordenador(request.user)


class ReadOnlyOrProfissionalDeSaude(permissions.BasePermission):
    """Escrita só para terapeuta e coordenador; leitura conforme o get_queryset."""

    def has_permission(self, request, view):
        if request.method in SAFE:
            return True
        return is_terapeuta(request.user) or is_coordenador(request.user)


class ProfissionalDeSaudeComEdicaoPropria(permissions.BasePermission):
    """Terapeuta cria anotações; edita/apaga só as que ele mesmo criou. Coordenador pode tudo."""

    def has_permission(self, request, view):
        if request.method in SAFE:
            return True
        return is_terapeuta(request.user) or is_coordenador(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE or is_coordenador(request.user):
            return True
        return obj.created_by_id == request.user.pk


class IsCoordenador(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_coordenador(request.user)


class IsSelfOrRecepcaoOuCoordenador(permissions.BasePermission):
    """
    Usuário edita o próprio cadastro; recepção e coordenador editam qualquer um;
    só coordenador apaga; só recepção e coordenador criam.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return is_recepcao_ou_coordenador(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE:
            return True
        if request.method == 'DELETE':
            return is_coordenador(request.user)
        return obj.pk == request.user.pk or is_recepcao_ou_coordenador(request.user)
