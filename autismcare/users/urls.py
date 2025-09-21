from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AutenticationUserViewSet, AddressViewSet, RoleViewSet, EmployeeViewSet
from patients.views import ParentViewSet, ChildViewSet
from medical.views import AllergyViewSet, MedicalRecordViewSet, MedicalHistoryViewSet

router = DefaultRouter()
# Rotas do app 'users'
router.register(r'users', AutenticationUserViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'employees', EmployeeViewSet)

# Rotas do app 'patients'
router.register(r'parents', ParentViewSet)
router.register(r'children', ChildViewSet)

# Rotas do app 'medical'
router.register(r'allergies', AllergyViewSet)
router.register(r'medical-records', MedicalRecordViewSet)
router.register(r'medical-histories', MedicalHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]