from rest_framework import viewsets
from authentication.models.base import AutenticationUser, Address
from authentication.serializers.base_serializer import AutenticationUserSerializer, AddressSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class AutenticationUserViewSet(viewsets.ModelViewSet):
    queryset = AutenticationUser.objects.all()
    serializer_class = AutenticationUserSerializer