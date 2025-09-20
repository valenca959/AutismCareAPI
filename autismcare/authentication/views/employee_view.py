from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from authentication.models.employee import Employee
from authentication.serializers.employee_serializer import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]