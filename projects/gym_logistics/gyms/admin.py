from django.contrib import admin
from .models import (
    GymCompany, Branch, Trainer, GymClass,
    TrainerSalary, Member, ClassBooking, AttendanceLog, EquipmentAsset
)

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1

@admin.register(GymCompany)
class GymCompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'corporate_email', 'created_at', 'updated_at')  # Must match models.py
    search_fields = ['name', 'corporate_email']
    inlines = [BranchInline]
    
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'address', 'gym_company')  # Must match models.py
    list_filter = ('city', 'gym_company')                            # Must match models.py
    search_fields = ['address']
    
@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'specialty', 'ratings', 'display_branches')
    list_filter = ('specialty', 'branch')
    search_fields = ['first_name', 'last_name']
    
    def display_branches(self, obj):
        return ", ".join([bran.name for bran in obj.branch.all()])
    
    display_branches.short_description = 'Assigned Branches'
    
@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'class_overview', 'branch', 'trainer', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'branch', 'trainer')
    search_fields = ['name']
    
@admin.register(TrainerSalary)
class TrainerSalaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'trainer','gym_company','base_salary', 'hourly_bonus_rate')
    list_filter = ('gym_company',)
    search_fields = ['first_name', 'last_name']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'gym_company', 'joined_date')
    list_filter = ('gym_company',)
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(ClassBooking)
class ClassBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'gym_class', 'booking_timestamp')
    list_filter = ('gym_class',)
    search_fields = ['member__first_name', 'member__last_name', 'gym_class__name']

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_member', 'get_class', 'status', 'check_in_time')
    list_filter = ('status',)
    
    # Custom methods to display nested booking properties cleanly in the table columns
    def get_member(self, obj):
        return f"{obj.booking.member.first_name} {obj.booking.member.last_name}"
    get_member.short_description = 'Member'

    def get_class(self, obj):
        return obj.booking.gym_class.name
    get_class.short_description = 'Gym Class'

@admin.register(EquipmentAsset)
class EquipmentAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'serial_number', 'branch', 'condition_status', 'last_inspected_date')
    list_filter = ('condition_status', 'branch')
    search_fields = ['name', 'serial_number']