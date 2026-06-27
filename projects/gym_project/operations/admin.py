from django.contrib import admin
from .models import GymClass, ClassBooking, AttendanceLog, EquipmentAsset


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'day_of_week', 'start_time', 'end_time']
    list_filter = ['day_of_week', 'trainer']
    search_fields = ['name', 'trainer__user__first_name', 'trainer__user__last_name']
    
@admin.register(ClassBooking)
class ClassBookingAdmin(admin.ModelAdmin):
    list_display = ['member', 'gym_class', 'booking_timestamp']
    list_filter = ['gym_class', 'booking_timestamp']
    search_fields = ['member__user__first_name', 'member__user__last_name', 'gym_class__name']
    

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ['booking', 'check_in_time', 'status']
    list_filter = ['status']
    search_fields = ['booking__member__user__first_name', 'booking__member__user__last_name', 'booking__gym_class__name']
    

@admin.register(EquipmentAsset)
class EquipmentAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'condition_status']
    list_filter = ['condition_status']
    search_fields = ['name', 'serial_number']