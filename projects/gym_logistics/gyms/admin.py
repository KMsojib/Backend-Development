from django.contrib import admin
from .models import GymCompany, Branch, Trainer, GymClass

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
    list_display = ('id', 'first_name', 'last_name', 'specialty', 'ratings', 'branch')
    list_filter = ('specialty', 'branch')
    search_fields = ['first_name', 'last_name']
    
@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'class_overview', 'branch', 'trainer', 'Day_of_week', 'start_time', 'end_time')
    list_filter = ('Day_of_week', 'branch', 'trainer')
    search_fields = ['name']