from rest_framework import permissions
from .models import StaffProfile
class IsManagerOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            profile = request.user.staffprofile
            return profile.role in ['MANAGER', 'OWNER']
        except StaffProfile.DoesNotExist:
            return False