from django.urls import path
from .views import ClassBookingCreateAPIView

urlpatterns = [
    path('bookings/create/', ClassBookingCreateAPIView.as_view(), name='booking-create'),
]