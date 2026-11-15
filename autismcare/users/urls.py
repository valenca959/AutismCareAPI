from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    AuthenticationUserViewSet,
    AddressViewSet,
    RoleViewSet,
    EmployeeViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from patients.views import ParentViewSet, ChildViewSet, AgendamentoViewSet
from medical.views import (
    AllergyViewSet,
    MedicalRecordViewSet,
    MedicalHistoryViewSet,
    RegistroAcessoViewSet,
)

router = DefaultRouter()
# basename é obrigatório porque as views filtram por get_queryset()

# Rotas do app 'users'
router.register(r'users', AuthenticationUserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'employees', EmployeeViewSet, basename='employee')

# Rotas do app 'patients'
router.register(r'parents', ParentViewSet, basename='parent')
router.register(r'children', ChildViewSet, basename='child')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

# Rotas do app 'medical'
router.register(r'allergies', AllergyViewSet, basename='allergy')
router.register(r'medical-records', MedicalRecordViewSet, basename='medical-record')
router.register(r'medical-histories', MedicalHistoryViewSet, basename='medical-history')
router.register(r'acessos-medicos', RegistroAcessoViewSet, basename='acesso-medico')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
