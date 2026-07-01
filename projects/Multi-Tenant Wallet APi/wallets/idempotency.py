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

            # If no key is provided, bypass idempotency tracking and run normally
            if not idem_key:
                return view_func(view_instance, request, *args, **kwargs)


            # Attempt to reserve this key for the active tenant context
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

            # Execute actual view logic if the key reservation was successful
            response = view_func(view_instance, request, *args, **kwargs)

            # Commit the evaluated response data back to the key history for future replays
            if response.status_code >= 200 and response.status_code < 300:
                record.response_status = response.status_code
                record.response_body = response.data
                record.save()
            else:
                # Rollback/delete the key track if the action failed structurally (4xx/5xx)
                record.delete()

            return response
        return _wrapped_view
    return decorator