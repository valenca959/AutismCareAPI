from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import AllergyViewSet, MedicalRecordViewSet, MedicalHistoryViewSet, RegistroAcessoViewSet

router = SimpleRouter()
router.register(r'allergies', AllergyViewSet, basename='allergy')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'medical-histories', MedicalHistoryViewSet, basename='medical-history')
router.register(r'acessos-medicos', RegistroAcessoViewSet, basename='acesso-medico')

urlpatterns = [
    path('', include(router.urls)),
]
