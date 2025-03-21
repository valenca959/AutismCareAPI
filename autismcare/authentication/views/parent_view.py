from rest_framework import viewsets
from authentication.models.parent import Parent
from authentication.serializers.parent_serializer import ParentSerializer

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer