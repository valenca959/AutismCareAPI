from django.urls import reverse

from autismcare.cenarios import BaseCenario
from users.models import AuthenticationUser
from .models import MedicalHistory, RegistroAcesso


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


class AdminAuditoriaTest(BaseCenario):
    def test_registro_de_acesso_e_somente_leitura_no_admin(self):
        admin_user = AuthenticationUser.objects.create_superuser(
            email='admin@x.com', password='senha-forte-123', cpf='72313403424', telephone='+5581999993333',
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
            email='admin@x.com', password='senha-forte-123', cpf='72313403424', telephone='+5581999993333',
        )
        self.client.force_login(admin_user)
        for url in [
            '/admin/users/authenticationuser/', '/admin/users/employee/', '/admin/users/address/',
            '/admin/users/role/', '/admin/patients/parent/', '/admin/patients/child/',
            '/admin/patients/agendamento/', '/admin/medical/allergy/', '/admin/medical/medicalrecord/',
            '/admin/medical/medicalhistory/', f'/admin/patients/parent/{self.resp.pk}/change/',
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
