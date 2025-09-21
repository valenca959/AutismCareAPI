from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import AutenticationUser, Address, Role, Employee
from .serializers import AutenticationUserSerializer, AddressSerializer, RoleSerializer, EmployeeSerializer
from .permissions import IsOwnerOrReadOnly

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAdminUser]

class AutenticationUserViewSet(viewsets.ModelViewSet):
    queryset = AutenticationUser.objects.select_related('address')
    serializer_class = AutenticationUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'role')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]