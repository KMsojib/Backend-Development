from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AuthViewSet

register_action = AuthViewSet.as_view({'post':'register'})

urlpatterns = [
    path('register/', register_action, name = 'auth-register'),
    path('login/', TokenObtainPairView.as_view(),name ='token-obtain-auth'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token-refresh',)
]
