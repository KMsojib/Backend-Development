from django.urls import path
from gyms.views import (
    GymCompanyListCreateAPIView, GymCompanyDetailAPIView,
    BranchListCreateAPIView, BranchDetailAPIView,
    TrainerListCreateAPIView, TrainerDetailAPIView,
    GymClassListCreateAPIView, GymClassDetailAPIView,
    TrainerSalaryAPIView, AttendanceStatusToggleAPIView,
    EquipmentBranchInventoryAPIView, ClassBookingCreateAPIView,
    MemberListCreateAPIView, MemberDetailAPIView,
)

urlpatterns = [
    # 🏢 Company Routes (api/ stripped out)
    path('companies/', GymCompanyListCreateAPIView.as_view(), name='company-list'),
    path('companies/<int:pk>/', GymCompanyDetailAPIView.as_view(), name='company-detail'),
    
    # 📍 Branch Routes
    path('branches/', BranchListCreateAPIView.as_view(), name='branch-list'),
    path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),
    
    # 👥 Member Routes (Added missing trailing slash here)
    path('members/', MemberListCreateAPIView.as_view(), name='member-list'),
    path('members/<int:pk>/', MemberDetailAPIView.as_view(), name='member-detail'),
    
    # 🏋️ Trainer Routes
    path('trainers/', TrainerListCreateAPIView.as_view(), name='trainer-list'),
    path('trainers/<int:pk>/', TrainerDetailAPIView.as_view(), name='trainer-detail'),
    path('trainers/<int:trainer_id>/salary/', TrainerSalaryAPIView.as_view(), name='trainer-salary-secure'),    
    
    # ⏱️ Class & Booking Routes
    path('classes/', GymClassListCreateAPIView.as_view(), name='class-list'),
    path('classes/<int:pk>/', GymClassDetailAPIView.as_view(), name='class-detail'),
    path('bookings/create/', ClassBookingCreateAPIView.as_view(), name='class-booking-safeguard'),
    
    # 🔄 Attendance Logs
    path('attendance/<int:log_id>/toggle/', AttendanceStatusToggleAPIView.as_view(), name='attendance-toggle'),
    
    # 📦 Asset Management
    path('branches/<int:branch_id>/equipment/', EquipmentBranchInventoryAPIView.as_view(), name='branch-assets'),
]