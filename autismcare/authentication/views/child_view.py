from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from authentication.models.child import Child
from authentication.serializers.child_serializer import ChildSerializer
from authentication.permissions import IsParentOrReadOnly

class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated, IsParentOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'parent'):
            return Child.objects.filter(parent=user.parent)
        elif hasattr(user, 'employee'):
            return Child.objects.all()
        return Child.objects.none()