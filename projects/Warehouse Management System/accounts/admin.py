from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomeUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_display_links = ('id','email')
    list_filter = ('role','is_staff','is_active')
   
    search_fields = ('email',)
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('WMS Authorizations & Roles', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Audit Timestamps', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('toggle',),
            'fields': ('email', 'password', 'role', 'is_staff', 'is_active'),
        }),
    )
    