import hashlib
import hmac

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


def _fernet():
    return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())


def hash_cpf(cpf):
    """HMAC do CPF. Serve para unicidade e busca sem guardar o CPF em texto."""
    chave = hashlib.sha256(settings.FIELD_ENCRYPTION_KEY.encode()).digest()
    return hmac.new(chave, cpf.encode(), hashlib.sha256).hexdigest()


class _CriptografiaMixin:
    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            # Valor antigo, ainda em texto puro. Só ocorre antes da migração de dados rodar.
            return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return _fernet().encrypt(str(value).encode()).decode()


class EncryptedCharField(_CriptografiaMixin, models.CharField):
    pass


class EncryptedTextField(_CriptografiaMixin, models.TextField):
    pass
