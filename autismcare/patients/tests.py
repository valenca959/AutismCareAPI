from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import AutenticationUser
from .models import Parent, Child
from datetime import date # Importe o 'date' para criar uma data

class PatientPermissionsTests(APITestCase):
    def setUp(self):
        self.user1 = AutenticationUser.objects.create_user(email='pai1@example.com', password='password', cpf='11111111111')
        self.parent1 = Parent.objects.create(user=self.user1)

        self.user2 = AutenticationUser.objects.create_user(email='pai2@example.com', password='password', cpf='22222222222')
        self.parent2 = Parent.objects.create(user=self.user2)

        self.child1 = Child.objects.create(
            parent=self.parent1,
            first_name='Filho',
            last_name='Um',
            birthdate=date(2020, 5, 15) # Adicionamos uma data de exemplo
        )

    def test_parent_cannot_see_other_parents_children(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('child-detail', kwargs={'pk': self.child1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_parent_can_see_own_children(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('child-detail', kwargs={'pk': self.child1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.child1.first_name)