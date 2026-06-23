from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseInventoryViewSet, InventoryTransferAPIView, SupplierAPIViewSet,InventoryItemViewSet
router = DefaultRouter()
router.register(r'warehouses',WarehouseInventoryViewSet,basename="warehouse-inventory")
router.register(r'suppliers',SupplierAPIViewSet,basename="supplier")
router.register(r'items',InventoryItemViewSet,basename='inventory-item')

urlpatterns = [
    path('',include(router.urls)),
    path('transfer/',InventoryTransferAPIView.as_view(),name='inventory-transfer'),
]
