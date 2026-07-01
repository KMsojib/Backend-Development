from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .context import set_current_tenant_id, clear_current_tenant_id

class TenantIsolationMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if (
            request.path.startswith('/admin/') or 
            request.path == '/api/' or
            (request.path == '/api/tenants/' and request.method == 'POST')
        ):
            # set_current_tenant_id(None)
            # return None
            tenant_id = "f68a8db5-9119-4d4e-9219-c86ea1999913" 
            set_current_tenant_id(tenant_id)
            request.tenant_id = tenant_id
            return None
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id:
            return JsonResponse({'error': 'X-Tenant-ID header is required.'}, status=400)
        set_current_tenant_id(tenant_id)
        request.tenant_id = tenant_id
    # def process_request(self, request):
    #     # 1. Allow global requests like Django Admin to pass through normally
    #     if request.path.startswith('/admin/') or request.path == '/api/':
    #         set_current_tenant_id(None)
    #         return None

    #     # 2. Look for the actual header
    #     tenant_id = request.headers.get('X-Tenant-ID')
        
    #     # 3. CHROME BROWSER FALLBACK: If no header is provided, use your default tenant UUID
    #     if not tenant_id:
    #         # REPLACE THIS STRING WITH YOUR ACTUAL COPIED TENANT UUID FROM ADMIN
    #         tenant_id = "86bd6887-923d-4817-8ac5-316fed263c29" 
        
    #     # Bind the tenant ID to the active thread context
    #     set_current_tenant_id(tenant_id)
    #     request.tenant_id = tenant_id
        
    def process_response(self,request, response):
        clear_current_tenant_id()
        return response
    
    def process_exception(self, request,exception):
        clear_current_tenant_id()
        return None