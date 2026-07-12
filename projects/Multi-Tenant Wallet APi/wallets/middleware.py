from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .context import set_current_tenant_id, clear_current_tenant_id
from .models import Tenant

class TenantIsolationMiddleware(MiddlewareMixin):
    IS_DEVELOPMENT = True 

    def process_request(self, request):
        if request.path.startswith('/admin/'):
            set_current_tenant_id(None)
            return None

        tenant_id = request.headers.get('X-Tenant-ID')

        if not tenant_id:
            if self.IS_DEVELOPMENT:
                first_tenant = Tenant.objects.first()
                if first_tenant:
                    tenant_id = str(first_tenant.id)
                else:
                    tenant_id = "f68a8db5-9119-4d4e-9219-c86ea1999913" 
            else:
                if request.path == '/api/' or (request.path == '/api/tenants/' and request.method == 'POST'):
                    set_current_tenant_id(None)
                    return None
                return JsonResponse({'error': 'X-Tenant-ID header is required.'}, status=400)

        set_current_tenant_id(tenant_id)
        request.tenant_id = tenant_id
        return None
        
    def process_response(self, request, response):
        clear_current_tenant_id()
        return response
    
    def process_exception(self, request, exception):
        clear_current_tenant_id()
        return None