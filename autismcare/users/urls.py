from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from .views import (
    AuthenticationUserViewSet,
    AddressViewSet,
    RoleViewSet,
    EmployeeViewSet,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

router = SimpleRouter()
# basename é obrigatório porque as views filtram por get_queryset()
router.register(r'users', AuthenticationUserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/logout/', TokenBlacklistView.as_view(), name='token_logout'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
