from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from authentication.models.role import Role
from authentication.serializers.role_serializer import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]