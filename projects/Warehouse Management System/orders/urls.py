from django.urls import path
from .views import OrderViewSet

order_list = OrderViewSet.as_view({'get': 'list', 'post': 'create'})
order_detail = OrderViewSet.as_view({'get': 'retrieve'})
order_approve = OrderViewSet.as_view({'post': 'approve'})
order_cancel = OrderViewSet.as_view({'post': 'cancel'})
order_complete = OrderViewSet.as_view({'post': 'complete'})

urlpatterns = [
    path('', order_list, name='order-list'),
    path('<int:pk>/', order_detail, name='order-detail'),
    path('<int:pk>/approve/', order_approve, name='order-approve'),
    path('<int:pk>/cancel/', order_cancel, name='order-cancel'),
    path('<int:pk>/complete/', order_complete, name='order-complete'),
]