# from django.contrib import admin
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter  # type: ignore
# from gyms.views import GymCompanyViewSet, GymClassViewSet, BranchViewSet, TrainerviewSet

# # The router dynamically tracks and constructs all GET, POST, PUT, DELETE URL segments
# router = DefaultRouter()
# router.register(r'companies', GymCompanyViewSet, basename='gym')
# router.register(r'classes', GymClassViewSet, basename='gymclass')
# router.register(r'branches', BranchViewSet, basename='branch')
# router.register(r'trainers', TrainerviewSet, basename='trainer')

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include(router.urls)),  # Mount all routes onto the /api/ prefix
# ]

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gyms.views import (
    GymCompanyListCreateAPIView, GymCompanyDetailAPIView,
    BranchListCreateAPIView, BranchDetailAPIView,
    TrainerListCreateAPIView, TrainerDetailAPIView,
    GymClassListCreateAPIView, GymClassDetailAPIView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Company Manual Routes
    path('api/companies/', GymCompanyListCreateAPIView.as_view(), name='company-list'),
    path('api/companies/<int:pk>/', GymCompanyDetailAPIView.as_view(), name='company-detail'),
    
    # Branch Manual Routes
    path('api/branches/', BranchListCreateAPIView.as_view(), name='branch-list'),
    path('api/branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),
    
    # Trainer Manual Routes
    path('api/trainers/', TrainerListCreateAPIView.as_view(), name='trainer-list'),
    path('api/trainers/<int:pk>/', TrainerDetailAPIView.as_view(), name='trainer-detail'),
    
    # Class Manual Routes
    path('api/classes/', GymClassListCreateAPIView.as_view(), name='class-list'),
    path('api/classes/<int:pk>/', GymClassDetailAPIView.as_view(), name='class-detail'),
]