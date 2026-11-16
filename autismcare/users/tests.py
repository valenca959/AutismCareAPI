from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.db import connection
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from autismcare.cenarios import BaseCenario, criar_usuario, emails_da_resposta
from medical.models import MedicalHistory
from .cpf import cpf_valido
from .models import AuthenticationUser, Role, Employee


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


class CadastroSenhaTest(BaseCenario):
    def test_recepcao_cria_usuario_sem_senha_e_envia_email(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('user-list'), {
            'email': 'novo@x.com',
            'cpf': '94579619196',
            'telephone': '+5581999991111',
            'first_name': 'Novo',
            'last_name': 'Responsavel',
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(AuthenticationUser.objects.get(email='novo@x.com').has_usable_password())

    def test_confirma_senha_com_token(self):
        user = criar_usuario('novo2@x.com', '48355511255')
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
        user = criar_usuario('cpf@x.com', '81194205194')
        with connection.cursor() as cursor:
            cursor.execute('SELECT cpf FROM users_authenticationuser WHERE id = %s', [user.pk])
            bruto = cursor.fetchone()[0]
        self.assertNotIn('81194205194', bruto)
        user.refresh_from_db()
        self.assertEqual(user.cpf, '81194205194')

    def test_cpf_duplicado_retorna_400(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('user-list'), {
            'email': 'dup@x.com', 'cpf': '14145190793', 'telephone': '+5581999992222',
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
        self.assertNotEqual(self.resp.user.cpf, '31855740877')
        self.assertEqual(MedicalHistory.objects.filter(child=self.crianca).count(), 1)

    def test_anonimizar_so_coordenador(self):
        self.client.force_authenticate(self.recepcao.user)
        resp = self.client.post(reverse('user-anonimizar', args=[self.resp.user.pk]))
        self.assertEqual(resp.status_code, 403)


class CadastroFuncionarioTest(BaseCenario):
    def test_coordenador_cadastra_funcionario(self):
        user = criar_usuario('novo-func@x.com', '30289797055')
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
            email='admin@x.com', password='senha-forte-123', cpf='72313403424', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        resp = self.client.post('/admin/users/authenticationuser/add/', {
            'email': 'pelo-admin@x.com', 'cpf': '19857291724', 'telephone': '+5581999994444',
            'usable_password': 'true', 'password1': 'Senha-forte-789', 'password2': 'Senha-forte-789',
        })
        self.assertEqual(resp.status_code, 302)
        user = AuthenticationUser.objects.get(email='pelo-admin@x.com')
        self.assertNotEqual(user.password, 'Senha-forte-789')
        self.assertTrue(user.check_password('Senha-forte-789'))

    def test_admin_recusa_cpf_duplicado(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='72313403424', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        resp = self.client.post('/admin/users/authenticationuser/add/', {
            'email': 'dup-admin@x.com', 'cpf': '14145190793', 'telephone': '+5581999994444',
            'usable_password': 'true', 'password1': 'Senha-forte-789', 'password2': 'Senha-forte-789',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(AuthenticationUser.objects.filter(email='dup-admin@x.com').exists())

    def test_admin_abre_pagina_de_edicao(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='72313403424', telephone='+5581999993333',
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


class LogoutTest(BaseCenario):
    def setUp(self):
        super().setUp()
        cache.clear()
        resp = self.client.post(reverse('token_obtain_pair'), {'email': 'resp@x.com', 'password': 'senha-forte-123'})
        self.refresh = resp.data['refresh']

    def test_logout_invalida_o_refresh(self):
        resp = self.client.post(reverse('token_logout'), {'refresh': self.refresh})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(reverse('token_refresh'), {'refresh': self.refresh})
        self.assertEqual(resp.status_code, 401)

    def test_refresh_gira_e_o_antigo_deixa_de_valer(self):
        resp = self.client.post(reverse('token_refresh'), {'refresh': self.refresh})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('refresh', resp.data)
        self.assertNotEqual(resp.data['refresh'], self.refresh)
        resp = self.client.post(reverse('token_refresh'), {'refresh': self.refresh})
        self.assertEqual(resp.status_code, 401)


class CpfTest(BaseCenario):
    def _cadastrar(self, cpf):
        self.client.force_authenticate(self.recepcao.user)
        return self.client.post(reverse('user-list'), {
            'email': 'cpf-novo@x.com', 'cpf': cpf, 'telephone': '+5581999995555',
            'first_name': 'Teste', 'last_name': 'Cpf',
        })

    def test_cpf_com_digito_errado_e_recusado(self):
        resp = self._cadastrar('52998224724')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('cpf', resp.data)

    def test_cpf_com_digitos_repetidos_e_recusado(self):
        self.assertEqual(self._cadastrar('11111111111').status_code, 400)

    def test_cpf_com_pontuacao_e_aceito_e_normalizado(self):
        resp = self._cadastrar('529.982.247-25')
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(AuthenticationUser.objects.get(email='cpf-novo@x.com').cpf, '52998224725')

    def test_cpf_duplicado_com_pontuacao_e_recusado(self):
        self.resp.user.cpf = '52998224725'
        self.resp.user.save()
        resp = self._cadastrar('529.982.247-25')
        self.assertEqual(resp.status_code, 400)

    def test_anonimizacao_gera_cpf_valido(self):
        self.client.force_authenticate(self.coordenador.user)
        self.client.post(reverse('user-anonimizar', args=[self.resp.user.pk]))
        self.resp.user.refresh_from_db()
        self.assertTrue(cpf_valido(self.resp.user.cpf))


class MascaraCpfTest(BaseCenario):
    def _cpf_do_responsavel_visto_por(self, quem):
        self.client.force_authenticate(quem)
        return self.client.get(reverse('user-detail', args=[self.resp.user.pk])).data['cpf']

    def test_terapeuta_ve_cpf_mascarado(self):
        cpf = self._cpf_do_responsavel_visto_por(self.terapeuta.user)
        self.assertEqual(cpf, '***.***.***-' + self.resp.user.cpf[-2:])

    def test_recepcao_ve_cpf_completo(self):
        self.assertEqual(self._cpf_do_responsavel_visto_por(self.recepcao.user), self.resp.user.cpf)

    def test_proprio_usuario_ve_cpf_completo(self):
        self.client.force_authenticate(self.resp.user)
        self.assertEqual(self.client.get(reverse('user-me')).data['cpf'], self.resp.user.cpf)

    def test_cpf_mascarado_tambem_dentro_da_crianca(self):
        self.client.force_authenticate(self.terapeuta.user)
        resp = self.client.get(reverse('child-detail', args=[self.crianca.pk]))
        self.assertTrue(resp.data['parent_detail']['cpf'].startswith('***'))
