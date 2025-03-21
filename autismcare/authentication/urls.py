from django.urls import path, include
from rest_framework.routers import DefaultRouter
from authentication.views.base_view import AutenticationUserViewSet, AddressViewSet
from authentication.views.role_view import RoleViewSet
from authentication.views.employee_view import EmployeeViewSet
from authentication.views.parent_view import ParentViewSet
from authentication.views.child_view import ChildViewSet
from authentication.views.medical_view import AllergyViewSet, MedicalRecordViewSet, MedicalHistoryViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', AutenticationUserViewSet)         # Usuários autenticados
router.register(r'addresses', AddressViewSet)               # Endereços
router.register(r'roles', RoleViewSet)                      # Funções
router.register(r'employees', EmployeeViewSet)              # Funcionários
router.register(r'parents', ParentViewSet)                  # Pais/Responsáveis
router.register(r'children', ChildViewSet)                  # Crianças
router.register(r'allergies', AllergyViewSet)               # Alergias
router.register(r'medical-records', MedicalRecordViewSet)   # Prontuários médicos
router.register(r'medical-histories', MedicalHistoryViewSet) # Históricos médicos

urlpatterns = [
    path('', include(router.urls)),                          # Inclui todas as rotas do router
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),    # Obter token JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   # Atualizar token JWT
]