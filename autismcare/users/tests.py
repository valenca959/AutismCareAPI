from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import AutenticationUser

class UserAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = AutenticationUser.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            cpf='12345678901'
        )
        self.list_users_url = reverse('autenticationuser-list') 

    def test_unauthenticated_user_cannot_access_users_list(self):
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_access_users_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)