import uuid
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .context import set_current_tenant_id, clear_current_tenant_id
from .models import Tenant

class TenantIsolationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        normalized_path = request.path.rstrip('/')
        
        if (
            request.path.startswith('/admin/') or 
            request.path.startswith('/api/schema/') or 
            request.path.startswith('/api/docs/')
        ):
            set_current_tenant_id(None)
            return None

        tenant_id = request.headers.get('X-Tenant-ID')

        if not tenant_id:
            if settings.DEBUG:
                first_tenant = Tenant.objects.first()
                if first_tenant:
                    tenant_id = str(first_tenant.id)
                else:
                    tenant_id = "f68a8db5-9119-4d4e-9219-c86ea1999913" 
            else:
                if normalized_path in ['/api', '/api/tenants']:
                    set_current_tenant_id(None)
                    return None
                    
                return JsonResponse(
                    {'error': 'Security Exception: Multi-tenant boundary breach. X-Tenant-ID header is missing.'}, 
                    status=400
                )
        
        try:
            uuid.UUID(tenant_id)
        except ValueError:
            return JsonResponse(
                {'error': 'Bad Request: Invalid X-Tenant-ID UUID structure format.'}, 
                status=400
            )
        
        set_current_tenant_id(tenant_id)
        request.tenant_id = tenant_id
        return None
        
    def process_response(self, request, response):
        clear_current_tenant_id()
        return response
    
    def process_exception(self, request, exception):
        clear_current_tenant_id()
        return None