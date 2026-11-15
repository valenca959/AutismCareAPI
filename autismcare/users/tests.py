from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase

from medical.models import Allergy, MedicalHistory, RegistroAcesso
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
    return {item['email'] for item in response.data['results']}


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
        self.assertEqual(resp.data['count'], 0)

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
        self.assertEqual(self.client.get(reverse('medical-history-list')).data['count'], 1)
        self.client.force_authenticate(self.outro_resp.user)
        self.assertEqual(self.client.get(reverse('medical-history-list')).data['count'], 0)

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


class CadastroParentEmployeeTest(BaseCenario):
    def test_recepcao_cadastra_responsavel(self):
        user = criar_usuario('novo-resp@x.com', '10101010101')
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('parent-list'), {'user_id': user.pk, 'spouse': 'Carlos'})
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['user']['email'], 'novo-resp@x.com')
        self.assertTrue(Parent.objects.filter(user=user).exists())

    def test_funcionario_nao_vira_responsavel(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('parent-list'), {'user_id': self.terapeuta.user.pk})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('user_id', resp.data)

    def test_responsavel_duplicado_retorna_400(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('parent-list'), {'user_id': self.resp.user.pk})
        self.assertEqual(resp.status_code, 400)

    def test_coordenador_cadastra_funcionario(self):
        user = criar_usuario('novo-func@x.com', '20202020202')
        role = Role.objects.get(name='terapeuta')
        self.client.force_authenticate(self.coordenador.user)
        resp = self.client.post(reverse('employee-list'), {
            'user_id': user.pk, 'role_id': role.pk, 'salary': '2500.00', 'admission_date': '2025-01-01',
        })
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['role']['name'], 'terapeuta')
        self.assertEqual(Employee.objects.get(user=user).role, role)

    def test_responsavel_nao_vira_funcionario(self):
        self.client.force_authenticate(self.coordenador.user)
        resp = self.client.post(reverse('employee-list'), {
            'user_id': self.resp.user.pk, 'salary': '1000.00', 'admission_date': '2025-01-01',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('user_id', resp.data)


class AdminUsuarioTest(BaseCenario):
    def test_admin_cria_usuario_com_senha_em_hash(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='30303030303', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        resp = self.client.post('/admin/users/authenticationuser/add/', {
            'email': 'pelo-admin@x.com', 'cpf': '40404040404', 'telephone': '+5581999994444',
            'usable_password': 'true', 'password1': 'Senha-forte-789', 'password2': 'Senha-forte-789',
        })
        self.assertEqual(resp.status_code, 302)
        user = AuthenticationUser.objects.get(email='pelo-admin@x.com')
        self.assertNotEqual(user.password, 'Senha-forte-789')
        self.assertTrue(user.check_password('Senha-forte-789'))

    def test_admin_recusa_cpf_duplicado(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='30303030303', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        resp = self.client.post('/admin/users/authenticationuser/add/', {
            'email': 'dup-admin@x.com', 'cpf': '22222222222', 'telephone': '+5581999994444',
            'usable_password': 'true', 'password1': 'Senha-forte-789', 'password2': 'Senha-forte-789',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(AuthenticationUser.objects.filter(email='dup-admin@x.com').exists())

    def test_admin_abre_pagina_de_edicao(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='30303030303', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        resp = self.client.get(f'/admin/users/authenticationuser/{self.resp.user.pk}/change/')
        self.assertEqual(resp.status_code, 200)


class LoginEMeTest(BaseCenario):
    def setUp(self):
        super().setUp()
        cache.clear()  # o limite de tentativas fica no cache

    def test_login_retorna_tokens(self):
        resp = self.client.post(reverse('token_obtain_pair'), {
            'email': 'resp@x.com', 'password': 'senha-forte-123',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_login_bloqueia_apos_muitas_tentativas(self):
        for _ in range(10):
            resp = self.client.post(reverse('token_obtain_pair'), {'email': 'resp@x.com', 'password': 'errada'})
            self.assertEqual(resp.status_code, 401)
        resp = self.client.post(reverse('token_obtain_pair'), {'email': 'resp@x.com', 'password': 'errada'})
        self.assertEqual(resp.status_code, 429)

    def test_me_retorna_usuario_logado(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.get(reverse('user-me'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], 'ter@x.com')
        self.assertEqual(resp.data['user_type'], 'employee')

    def test_me_de_responsavel(self):
        self.client.force_authenticate(self.resp.user)
        resp = self.client.get(reverse('user-me'))
        self.assertEqual(resp.data['user_type'], 'parent')

    def test_me_exige_login(self):
        resp = self.client.get(reverse('user-me'))
        self.assertEqual(resp.status_code, 401)

    def test_me_com_token_jwt(self):
        token = self.client.post(reverse('token_obtain_pair'), {
            'email': 'resp@x.com', 'password': 'senha-forte-123',
        }).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.get(reverse('user-me'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], 'resp@x.com')


class AdminAuditoriaTest(BaseCenario):
    def test_registro_de_acesso_e_somente_leitura_no_admin(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='30303030303', telephone='+5581999993333',
        )
        registro = RegistroAcesso.objects.create(usuario=admin_user, recurso='prontuario', acao='leitura')
        self.client.force_login(admin_user)
        self.assertEqual(self.client.get('/admin/medical/registroacesso/').status_code, 200)
        self.assertEqual(self.client.get('/admin/medical/registroacesso/add/').status_code, 403)
        resp = self.client.post(f'/admin/medical/registroacesso/{registro.pk}/delete/', {'post': 'yes'})
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(RegistroAcesso.objects.filter(pk=registro.pk).exists())

    def test_paginas_de_lista_do_admin_abrem(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='30303030303', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        for url in [
            '/admin/users/authenticationuser/', '/admin/users/employee/', '/admin/users/address/',
            '/admin/users/role/', '/admin/patients/parent/', '/admin/patients/child/',
            '/admin/patients/agendamento/', '/admin/medical/allergy/', '/admin/medical/medicalrecord/',
            '/admin/medical/medicalhistory/', f'/admin/patients/parent/{self.resp.pk}/change/',
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)


class PaginacaoCorsDocsTest(BaseCenario):
    def test_listagem_paginada(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.get(reverse('user-list'), {'page_size': 2})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(set(resp.data), {'count', 'next', 'previous', 'results'})
        self.assertEqual(len(resp.data['results']), 2)
        self.assertGreaterEqual(resp.data['count'], 5)
        self.assertIsNotNone(resp.data['next'])

    def test_page_size_tem_limite(self):
        for i in range(105):
            Allergy.objects.create(name=f'Alergia {i:03d}')
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.get(reverse('allergy-list'), {'page_size': 500})
        self.assertEqual(len(resp.data['results']), 100)

    def test_cors_libera_front_local(self):
        resp = self.client.options(
            reverse('token_obtain_pair'),
            HTTP_ORIGIN='http://localhost:3000',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        )
        self.assertEqual(resp['Access-Control-Allow-Origin'], 'http://localhost:3000')

    def test_cors_bloqueia_outra_origem(self):
        resp = self.client.get(reverse('user-list'), HTTP_ORIGIN='http://site-malicioso.com')
        self.assertNotIn('Access-Control-Allow-Origin', resp)

    def test_documentacao_publica(self):
        self.assertEqual(self.client.get(reverse('swagger-ui')).status_code, 200)
        schema = self.client.get(reverse('schema'))
        self.assertEqual(schema.status_code, 200)
        self.assertIn(b'/api/users/me/', schema.content)
        self.assertIn(b'/api/password/reset/', schema.content)
