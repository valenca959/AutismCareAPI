from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Parent, Child
from .serializers import ParentSerializer, ChildSerializer
from users.permissions import IsOwnerOrReadOnly, IsParentOrReadOnly

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if hasattr(self.request.user, 'employee'):
            return Parent.objects.select_related('user').prefetch_related('children')
        return Parent.objects.filter(user=self.request.user).select_related('user').prefetch_related('children')

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