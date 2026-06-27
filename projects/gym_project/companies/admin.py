from django.contrib import admin
from .models import *


@admin.register(GymCompany)
class GymCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'corporate_email', 'created_at')
    search_fields = ('name','corporate_email')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'gym_company')
    search_fields = ('name','city','gym_company')