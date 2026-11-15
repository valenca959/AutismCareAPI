import secrets

from django.db import transaction

from patients.models import Parent  # noqa: F401  (usado via user.parent)
from .fields import hash_cpf
from .models import AuthenticationUser

# Placeholder válido para o campo obrigatório de telefone.
TELEFONE_ANONIMO = '+5500000000000'


def _cpf_aleatorio():
    while True:
        cpf = ''.join(secrets.choice('0123456789') for _ in range(11))
        if not AuthenticationUser.objects.filter(cpf_hash=hash_cpf(cpf)).exists():
            return cpf


@transaction.atomic
def anonimizar_usuario(user):
    """
    Remove os dados pessoais do usuário e mantém o vínculo clínico (prontuário e agendamentos),
    porque o prontuário precisa ser guardado pelo prazo legal.
    """
    endereco = user.address
    user.address = None
    user.email = f'anonimizado-{user.pk}@removido.invalido'
    user.first_name = ''
    user.last_name = ''
    user.cpf = _cpf_aleatorio()
    user.telephone = TELEFONE_ANONIMO
    user.telephone2 = None
    user.birthdate = None
    user.is_active = False
    user.set_unusable_password()
    user.save()

    if endereco is not None:
        endereco.delete()

    parent = getattr(user, 'parent', None)
    if parent is not None:
        parent.spouse = None
        parent.spouse_phone = None
        parent.save()
