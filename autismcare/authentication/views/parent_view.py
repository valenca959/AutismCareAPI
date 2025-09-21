from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from authentication.models.parent import Parent
from authentication.serializers.parent_serializer import ParentSerializer
from authentication.permissions import IsOwnerOrReadOnly

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all() 
    
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if hasattr(self.request.user, 'employee'):
            return Parent.objects.select_related('user').prefetch_related('children')
        
        return Parent.objects.filter(user=self.request.user).select_related('user').prefetch_related('children')