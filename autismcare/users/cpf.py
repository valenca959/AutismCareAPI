"""Regras do CPF: normalização, dígitos verificadores, geração e máscara."""
import re
import secrets

from django.core.exceptions import ValidationError


def normalizar_cpf(valor):
    """Aceita '123.456.789-09' ou '12345678909' e devolve só os dígitos."""
    return re.sub(r'\D', '', str(valor or ''))


def _digito(base):
    peso_inicial = len(base) + 1
    soma = sum(int(d) * peso for d, peso in zip(base, range(peso_inicial, 1, -1)))
    resto = soma % 11
    return '0' if resto < 2 else str(11 - resto)


def cpf_valido(cpf):
    if not re.fullmatch(r'\d{11}', cpf or ''):
        return False
    if cpf == cpf[0] * 11:  # 000.000.000-00, 111.111.111-11... passam na conta, mas são inválidos
        return False
    return cpf[9] == _digito(cpf[:9]) and cpf[10] == _digito(cpf[:10])


def validar_cpf(valor):
    """Validador do campo: 11 dígitos e dígitos verificadores corretos."""
    if not re.fullmatch(r'\d{11}', valor or ''):
        raise ValidationError('CPF deve ter 11 dígitos numéricos.', code='cpf_formato')
    if not cpf_valido(valor):
        raise ValidationError('CPF inválido.', code='cpf_invalido')


def gerar_cpf():
    """CPF aleatório válido (usado na anonimização e nos testes)."""
    while True:
        base = ''.join(secrets.choice('0123456789') for _ in range(9))
        if base != base[0] * 9:
            break
    base += _digito(base)
    return base + _digito(base)


def mascarar_cpf(cpf):
    """'12345678909' -> '***.***.***-09'."""
    if not cpf or len(cpf) != 11:
        return None
    return f'***.***.***-{cpf[-2:]}'
