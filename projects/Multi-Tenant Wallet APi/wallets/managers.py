from django.db import models
from .context import get_current_tenant_id

class TenantScopedQuerySet(models.Model):
    def as_manager(cls):
        return TenantScopedManager.from_queryset(cls)

# class TenantScopedManager(models.Model):
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         tenant_id = get_current_tenant_id()
        
#         if tenant_id is not None:
#             return queryset.filter(tenant_id = tenant_id)
#         return queryset
class TenantScopedManager(models.Manager):
    def get_queryset(self):
        # Grab the normal base queryset first
        queryset = super().get_queryset()
        tenant_id = get_current_tenant_id()
        
        # If a tenant is active in the context, strictly enforce the isolation boundary
        if tenant_id is not None:
            return queryset.filter(tenant_id=tenant_id)
        return queryset