from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.parent import ParentViewSet, ChildViewSet, MedicalRecordViewSet, MedicalHistoryViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'parents', ParentViewSet)
router.register(r'children', ChildViewSet)
router.register(r'medical-records', MedicalRecordViewSet)
router.register(r'medical-histories', MedicalHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
