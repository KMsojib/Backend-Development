from django.db import models
from django.conf import settings

class AuditLog(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    object_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_identity = self.user.email if self.user else "SYSTEM ENGINE"
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {user_identity} -> {self.action}"