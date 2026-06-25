from django.urls import path
from .views import ProductViewSet

product_list = ProductViewSet.as_view({'get': 'list', 'post': 'create'})
product_detail = ProductViewSet.as_view({'get': 'retrieve'})
add_stock_action = ProductViewSet.as_view({'post': 'add_stock'})
remove_stock_action = ProductViewSet.as_view({'post': 'remove_stock'})

urlpatterns = [
    path('', product_list, name='product-list'),
    path('<int:pk>/', product_detail, name='product-detail'),
    path('<int:pk>/add-stock/', add_stock_action, name='product-add-stock'),
    path('<int:pk>/remove-stock/', remove_stock_action, name='product-remove-stock'),
]