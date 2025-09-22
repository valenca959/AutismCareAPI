# autismcare/medical/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import AutenticationUser, Employee, Role
from patients.models import Parent, Child
from datetime import date

class MedicalPermissionsTests(APITestCase):

    def setUp(self):
        parent_user = AutenticationUser.objects.create_user(email='pai@example.com', password='password', cpf='11122233344')
        self.parent = Parent.objects.create(user=parent_user)
        self.child = Child.objects.create(parent=self.parent, first_name='Criança', last_name='Teste', birthdate=date(2021, 1, 1))

        employee_user = AutenticationUser.objects.create_user(email='funcionario@example.com', password='password', cpf='55566677788')
        role = Role.objects.create(name='Terapeuta')
        self.employee = Employee.objects.create(user=employee_user, role=role, admission_date=date(2022, 1, 1), salary=5000)
        
        self.create_history_url = reverse('medicalhistory-list')

    def test_parent_cannot_create_medical_history(self):
        self.client.force_authenticate(user=self.parent.user)
        history_data = {
            # CORREÇÃO: Usar 'child_id' para enviar os dados
            'child_id': self.child.pk,
            'description': 'Tentativa de registo pelo pai.',
            'history_type': 'other'
        }
        response = self.client.post(self.create_history_url, history_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_can_create_medical_history(self):
        self.client.force_authenticate(user=self.employee.user)
        history_data = {
            # CORREÇÃO: Usar 'child_id' para enviar os dados
            'child_id': self.child.pk,
            'description': 'Registo da sessão de terapia.',
            'history_type': 'consultation'
        }
        response = self.client.post(self.create_history_url, history_data)
        
        # Agora o teste vai passar
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Registo da sessão de terapia.')
        # Verificamos também se o 'created_by' foi associado corretamente
        self.assertEqual(response.data['created_by'], self.employee.user.pk)