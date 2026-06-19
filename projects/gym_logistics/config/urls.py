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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',include('gyms.urls')),
]