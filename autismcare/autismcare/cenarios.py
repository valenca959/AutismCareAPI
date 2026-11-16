"""Cenário e utilitários compartilhados pelos testes de users, patients e medical."""
from django.utils import timezone
from rest_framework.test import APITestCase

from patients.models import Parent, Child, Agendamento
from users.cpf import gerar_cpf
from users.models import AuthenticationUser, Role, Employee


def criar_usuario(email, cpf=None, **extra):
    return AuthenticationUser.objects.create_user(
        email=email,
        password='senha-forte-123',
        cpf=cpf or gerar_cpf(),
        telephone='+5581999990000',
        **extra,
    )


def criar_funcionario(email, cpf, cargo, status='active'):
    user = criar_usuario(email, cpf)
    role, _ = Role.objects.get_or_create(name=cargo)
    return Employee.objects.create(
        user=user, role=role, salary=1000, admission_date='2024-01-01', status=status,
    )


def emails_da_resposta(response):
    return {item['email'] for item in response.data['results']}


class BaseCenario(APITestCase):
    def setUp(self):
        self.recepcao = criar_funcionario('rec@x.com', '33961719691', 'recepcionista')
        self.terapeuta = criar_funcionario('ter@x.com', '14145190793', 'terapeuta')
        self.coordenador = criar_funcionario('coord@x.com', '64401840160', 'coordenador')
        self.resp = Parent.objects.create(user=criar_usuario('resp@x.com', '31855740877'))
        self.outro_resp = Parent.objects.create(user=criar_usuario('resp2@x.com', '25439007725'))
        self.crianca = Child.objects.create(
            parent=self.resp, first_name='Ana', last_name='Silva', birthdate='2018-05-01',
        )
        self.crianca_sem_agenda = Child.objects.create(
            parent=self.outro_resp, first_name='Bia', last_name='Souza', birthdate='2019-02-02',
        )
        # Só a Ana está agendada com o terapeuta.
        Agendamento.objects.create(child=self.crianca, terapeuta=self.terapeuta, data_hora=timezone.now())
