from django.urls import reverse

from medical.models import Allergy
from .cenarios import BaseCenario


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
