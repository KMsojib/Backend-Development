from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView #type:ignore
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/companies/', include('companies.urls')),
#     path('api/users/', include('users.urls')),
#     path('api/operations/', include('operations.urls')),
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/companies/', include('companies.urls')),
    path('api/users/', include('users.urls')),
    path('api/operations/', include('operations.urls')),
    
    # 2. Documentation Schema Gateways
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # This renders the beautiful interactive UI dashboard:
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

