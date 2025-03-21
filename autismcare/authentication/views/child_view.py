from rest_framework import viewsets
from authentication.models.child import Child
from authentication.serializers.child_serializer import ChildSerializer

class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer