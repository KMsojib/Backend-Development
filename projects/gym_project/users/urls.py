from django.urls import path
from .views import TrainerListCreateAPIView, MemberListCreateAPIView

urlpatterns = [
    path('trainers/', TrainerListCreateAPIView.as_view(), name='trainer-list-create'),
    path('members/', MemberListCreateAPIView.as_view(), name='member-list-create'),
]