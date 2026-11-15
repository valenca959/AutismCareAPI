from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase

from medical.models import MedicalHistory, RegistroAcesso
from patients.models import Parent, Child, Agendamento
from .models import AuthenticationUser, Role, Employee


def criar_usuario(email, cpf, **extra):
    return AuthenticationUser.objects.create_user(
        email=email,
        password='senha-forte-123',
        cpf=cpf,
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
    return {item['email'] for item in response.data}


class BaseCenario(APITestCase):
    def setUp(self):
        self.recepcao = criar_funcionario('rec@x.com', '11111111111', 'recepcionista')
        self.terapeuta = criar_funcionario('ter@x.com', '22222222222', 'terapeuta')
        self.coordenador = criar_funcionario('coord@x.com', '44444444444', 'coordenador')
        self.resp = Parent.objects.create(user=criar_usuario('resp@x.com', '55555555555'))
        self.outro_resp = Parent.objects.create(user=criar_usuario('resp2@x.com', '66666666666'))
        self.crianca = Child.objects.create(
            parent=self.resp, first_name='Ana', last_name='Silva', birthdate='2018-05-01',
        )
        self.crianca_sem_agenda = Child.objects.create(
            parent=self.outro_resp, first_name='Bia', last_name='Souza', birthdate='2019-02-02',
        )
        # Só a Ana está agendada com o terapeuta.
        Agendamento.objects.create(child=self.crianca, terapeuta=self.terapeuta, data_hora=timezone.now())


class UsuariosTest(BaseCenario):
    def test_recepcao_ve_todos_os_usuarios(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.get(reverse('user-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue({'rec@x.com', 'ter@x.com', 'resp@x.com', 'resp2@x.com'} <= emails_da_resposta(resp))

    def test_terapeuta_ve_so_proprio_e_responsaveis_agendados(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.get(reverse('user-list'))
        self.assertEqual(emails_da_resposta(resp), {'ter@x.com', 'resp@x.com'})

    def test_responsavel_ve_so_o_proprio_cadastro(self):
        self.client.force_authenticate(self.resp.user)
        resp = self.client.get(reverse('user-list'))
        self.assertEqual(emails_da_resposta(resp), {'resp@x.com'})

    def test_funcionario_inativo_perde_acesso_especial(self):
        self.terapeuta.status = 'inactive'
        self.terapeuta.save()
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.get(reverse('user-list'))
        self.assertEqual(emails_da_resposta(resp), {'ter@x.com'})


class CriancasTest(BaseCenario):
    def test_recepcao_cria_crianca(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('child-list'), {
            'parent': self.resp.pk, 'first_name': 'Caio', 'last_name': 'Lima', 'birthdate': '2020-01-01',
        })
        self.assertEqual(resp.status_code, 201)

    def test_terapeuta_nao_cria_crianca(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.post(reverse('child-list'), {
            'parent': self.resp.pk, 'first_name': 'Caio', 'last_name': 'Lima', 'birthdate': '2020-01-01',
        })
        self.assertEqual(resp.status_code, 403)


class MedicoTest(BaseCenario):
    def setUp(self):
        super().setUp()
        self.anotacao = MedicalHistory.objects.create(
            child=self.crianca, description='Sessão tranquila', created_by=self.terapeuta.user,
        )

    def test_recepcao_nao_ve_anotacoes(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.get(reverse('medical-history-list'))
        self.assertEqual(len(resp.data), 0)

    def test_terapeuta_registra_para_crianca_agendada(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.post(reverse('medical-history-list'), {
            'child': self.crianca.pk, 'description': 'Nova sessão', 'history_type': 'class',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['created_by'], self.terapeuta.user.pk)

    def test_terapeuta_nao_registra_para_crianca_sem_agenda(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.post(reverse('medical-history-list'), {
            'child': self.crianca_sem_agenda.pk, 'description': 'Indevido', 'history_type': 'class',
        })
        self.assertEqual(resp.status_code, 403)

    def test_created_by_nao_vem_do_cliente(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.post(reverse('medical-history-list'), {
            'child': self.crianca.pk,
            'description': 'Tentativa',
            'history_type': 'class',
            'created_by': self.coordenador.user.pk,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['created_by'], self.terapeuta.user.pk)

    def test_responsavel_ve_so_anotacoes_do_proprio_filho(self):
        self.client.force_authenticate(self.resp.user)
        self.assertEqual(len(self.client.get(reverse('medical-history-list')).data), 1)
        self.client.force_authenticate(self.outro_resp.user)
        self.assertEqual(len(self.client.get(reverse('medical-history-list')).data), 0)

    def test_responsavel_nao_registra_anotacao(self):
        self.client.force_authenticate(self.resp.user)
        resp = self.client.post(reverse('medical-history-list'), {
            'child': self.crianca.pk, 'description': 'Indevido', 'history_type': 'class',
        })
        self.assertEqual(resp.status_code, 403)

    def test_leitura_gera_registro_de_acesso(self):
        antes = RegistroAcesso.objects.count()
        self.client.force_authenticate(self.terapeuta.user)
        self.client.get(reverse('medical-history-list'))
        self.assertEqual(RegistroAcesso.objects.count(), antes + 1)


class CadastroSenhaTest(BaseCenario):
    def test_recepcao_cria_usuario_sem_senha_e_envia_email(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('user-list'), {
            'email': 'novo@x.com',
            'cpf': '77777777777',
            'telephone': '+5581999991111',
            'first_name': 'Novo',
            'last_name': 'Responsavel',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(AuthenticationUser.objects.get(email='novo@x.com').has_usable_password())

    def test_confirma_senha_com_token(self):
        user = criar_usuario('novo2@x.com', '88888888888')
        user.set_unusable_password()
        user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        resp = self.client.post(reverse('password-reset-confirm'), {
            'uid': uid, 'token': token, 'new_password': 'Outra-senha-forte-456',
        })
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('Outra-senha-forte-456'))

    def test_token_invalido_e_recusado(self):
        resp = self.client.post(reverse('password-reset-confirm'), {
            'uid': 'abc', 'token': 'invalido', 'new_password': 'Outra-senha-forte-456',
        })
        self.assertEqual(resp.status_code, 400)


class LGPDTest(BaseCenario):
    def test_cpf_fica_criptografado_no_banco(self):
        user = criar_usuario('cpf@x.com', '12312312312')
        with connection.cursor() as cursor:
            cursor.execute('SELECT cpf FROM users_authenticationuser WHERE id = %s', [user.pk])
            bruto = cursor.fetchone()[0]
        self.assertNotIn('12312312312', bruto)
        user.refresh_from_db()
        self.assertEqual(user.cpf, '12312312312')

    def test_cpf_duplicado_retorna_400(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('user-list'), {
            'email': 'dup@x.com', 'cpf': '22222222222', 'telephone': '+5581999992222',
            'first_name': 'Dup', 'last_name': 'Licado',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('cpf', resp.data)

    def test_exclusao_direta_bloqueada(self):
        self.client.force_authenticate(self.coordenador.user)
        resp = self.client.delete(reverse('user-detail', args=[self.resp.user.pk]))
        self.assertEqual(resp.status_code, 405)

    def test_anonimizacao_remove_dados_e_mantem_prontuario(self):
        MedicalHistory.objects.create(child=self.crianca, description='Sessão', created_by=self.terapeuta.user)
        self.client.force_authenticate(self.coordenador.user)
        resp = self.client.post(reverse('user-anonimizar', args=[self.resp.user.pk]))
        self.assertEqual(resp.status_code, 200)
        self.resp.user.refresh_from_db()
        self.assertFalse(self.resp.user.is_active)
        self.assertNotIn('resp@x.com', self.resp.user.email)
        self.assertNotEqual(self.resp.user.cpf, '55555555555')
        self.assertEqual(MedicalHistory.objects.filter(child=self.crianca).count(), 1)

    def test_anonimizar_so_coordenador(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('user-anonimizar', args=[self.resp.user.pk]))
        self.assertEqual(resp.status_code, 403)
