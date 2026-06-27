from django.urls import path
from .views import GymCompanyListCreateAPIView,BranchListCreateAPIView
urlpatterns = [
    path('company/', GymCompanyListCreateAPIView.as_view(), name='company-list'),
    path('company/<int:pk>/,', GymCompanyListCreateAPIView.as_view(), name='company-detail'),
    
    path('branches/', BranchListCreateAPIView.as_view(), name='branch-list-create'),
    path('branches/<int:pk>/,', BranchListCreateAPIView.as_view(), name='branch-detail'),

]