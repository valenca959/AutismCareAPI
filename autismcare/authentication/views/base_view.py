from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from authentication.models.base import AutenticationUser, Address
from authentication.serializers.base_serializer import AutenticationUserSerializer, AddressSerializer
from authentication.permissions import IsOwnerOrReadOnly 

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAdminUser]

class AutenticationUserViewSet(viewsets.ModelViewSet):
    queryset = AutenticationUser.objects.select_related('address')
    serializer_class = AutenticationUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]