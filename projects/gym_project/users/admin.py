from django.contrib import admin
from .models import Trainer, TrainerSalary, Member

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'speciality', 'ratings')
    search_fields = ('first_name', 'last_name', 'speciality')
    list_filter = ('speciality','branches')
    
@admin.register(TrainerSalary)
class TrainerSalaryAdmin(admin.ModelAdmin): 
    list_display = ('trainer', 'gym_company', 'salary', 'date')
    search_fields = ('trainer__first_name', 'trainer__last_name', 'gym_company__name')
    list_filter = ('gym_company',)
    
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'gym_company', 'branch', 'trainer')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('first_name','last_name','gym_company', 'branch', 'trainer')
