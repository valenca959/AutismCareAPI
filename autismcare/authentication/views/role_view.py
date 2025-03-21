from rest_framework import viewsets
from authentication.models.role import Role
from authentication.serializers.role_serializer import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer