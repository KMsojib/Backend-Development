from functools import wraps
from django.db import IntegrityError, transaction
from rest_framework.response import Response #type:ignore
from .models import IdempotencyKey

def idempotent_endpoint():
    """Decorator to enforce tenant-scoped request idempotency."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            idem_key = request.headers.get('Idempotency-Key')
            tenant_id = getattr(request, 'tenant_id', None)

            if not idem_key:
                return view_func(view_instance, request, *args, **kwargs)
            try:
                with transaction.atomic(using='default'):
                    # Create placeholder record
                    record = IdempotencyKey.objects.create(
                        tenant_id=tenant_id,
                        key=idem_key,
                        response_status=102, # Processing status placeholder
                        response_body={"message": "Processing request"}
                    )
            except IntegrityError:
                # Key conflict found! Retrieve the completed response history payload
                existing_record = IdempotencyKey.objects.get(tenant_id=tenant_id, key=idem_key)
                return Response(existing_record.response_body, status=existing_record.response_status)

            response = view_func(view_instance, request, *args, **kwargs)

            if response.status_code >= 200 and response.status_code < 300:
                record.response_status = response.status_code
                record.response_body = response.data
                record.save()
            else:
                record.delete()

            return response
        return _wrapped_view
    return decorator