from django.urls import path, include
from rest_framework.routers import DefaultRouter #type:ignore
from .views import TenantViewSet, WalletViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('api/', include(router.urls)),
]