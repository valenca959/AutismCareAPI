from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import ParentViewSet, ChildViewSet, AgendamentoViewSet

router = SimpleRouter()
router.register(r'parents', ParentViewSet, basename='parent')
router.register(r'children', ChildViewSet, basename='child')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

urlpatterns = [
    path('', include(router.urls)),
]
