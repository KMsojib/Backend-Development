from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pos_engine.views import OrderViewSet
from online_ordering.views import CustomerCartViewSet
from business_website.views import PublicWebPageViewSet

router = DefaultRouter()
router.register(r'pos/orders', OrderViewSet)
router.register(r'online/carts', CustomerCartViewSet, basename='online-cart')
router.register(r'web/pages', PublicWebPageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/analytics/summary/', include('analytics_reporting.urls')), # Map analytics endpoint cleanly
]