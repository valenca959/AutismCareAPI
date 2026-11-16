from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from autismcare.cenarios import BaseCenario, criar_funcionario, criar_usuario
from .models import Parent


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


class CadastroResponsavelTest(BaseCenario):
    def test_recepcao_cadastra_responsavel(self):
        user = criar_usuario('novo-resp@x.com', '63690254027')
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


class AgendaTest(BaseCenario):
    def setUp(self):
        super().setUp()
        self.amanha_10h = (timezone.localtime() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
        self.client.force_authenticate(self.recepcao.user)

    def _agendar(self, inicio, child=None, terapeuta=None, duracao=60):
        return self.client.post(reverse('agendamento-list'), {
            'child': (child or self.crianca).pk,
            'terapeuta': (terapeuta or self.terapeuta).pk,
            'data_hora': inicio.isoformat(),
            'duracao_minutos': duracao,
        })

    def test_agenda_valida(self):
        resp = self._agendar(self.amanha_10h)
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['crianca_nome'], 'Ana Silva')
        self.assertIn('fim', resp.data)

    def test_so_terapeuta_pode_ser_agendado(self):
        resp = self._agendar(self.amanha_10h, terapeuta=self.recepcao)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('terapeuta', resp.data)

    def test_terapeuta_inativo_nao_pode_ser_agendado(self):
        self.terapeuta.status = 'inactive'
        self.terapeuta.save()
        self.assertEqual(self._agendar(self.amanha_10h).status_code, 400)

    def test_nao_agenda_no_passado(self):
        resp = self._agendar(timezone.now() - timedelta(hours=1))
        self.assertEqual(resp.status_code, 400)
        self.assertIn('data_hora', resp.data)

    def test_conflito_de_horario_do_terapeuta(self):
        self.assertEqual(self._agendar(self.amanha_10h).status_code, 201)
        resp = self._agendar(self.amanha_10h + timedelta(minutes=30), child=self.crianca_sem_agenda)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('terapeuta', str(resp.data['data_hora']))

    def test_conflito_de_horario_da_crianca(self):
        outro_ter = criar_funcionario('ter2@x.com', None, 'terapeuta')
        self.assertEqual(self._agendar(self.amanha_10h).status_code, 201)
        resp = self._agendar(self.amanha_10h + timedelta(minutes=45), terapeuta=outro_ter)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('criança', str(resp.data['data_hora']))

    def test_horarios_encostados_sao_permitidos(self):
        self.assertEqual(self._agendar(self.amanha_10h).status_code, 201)
        resp = self._agendar(self.amanha_10h + timedelta(minutes=60), child=self.crianca_sem_agenda)
        self.assertEqual(resp.status_code, 201, resp.data)

    def test_editar_o_proprio_agendamento_nao_conflita_com_ele_mesmo(self):
        criado = self._agendar(self.amanha_10h).data
        resp = self.client.patch(reverse('agendamento-detail', args=[criado['id']]), {'duracao_minutos': 90})
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_responsavel_ve_agenda_do_proprio_filho(self):
        self._agendar(self.amanha_10h)
        self.client.force_authenticate(self.resp.user)
        resp = self.client.get(reverse('agendamento-list'))
        self.assertEqual(resp.data['count'], 2)  # o do cenário + o novo
        self.client.force_authenticate(self.outro_resp.user)
        self.assertEqual(self.client.get(reverse('agendamento-list')).data['count'], 0)

    def test_responsavel_nao_cria_agendamento(self):
        self.client.force_authenticate(self.resp.user)
        self.assertEqual(self._agendar(self.amanha_10h).status_code, 403)
