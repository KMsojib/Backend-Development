import json
from functools import wraps
from django.db import IntegrityError, transaction
from rest_framework.response import Response  # type:ignore
from .models import IdempotencyKey
from rest_framework import status  # type:ignore
from rest_framework.renderers import JSONRenderer  # type:ignore

def idempotent_endpoint():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            idem_key = request.headers.get('Idempotency-Key') or request.headers.get('X-Idempotency-Key')
            tenant_id = getattr(request, 'tenant_id', None)

            if not idem_key or not tenant_id:
                return view_func(request, *args, **kwargs)
            
            # First Pass Check
            existing_record = IdempotencyKey.unscoped_objects.filter(tenant_id=tenant_id, key=idem_key).first()
            
            if existing_record:
                if existing_record.response_status == 102:
                    return Response(
                        {"error": "Concurrent Lock: This transaction execution path is currently processing. Please wait."},
                        status=status.HTTP_409_CONFLICT
                    )
                return Response(existing_record.response_body, status=existing_record.response_status)
            
            record = None
            record_id = None
            try:
                with transaction.atomic(using='default'):
                    record = IdempotencyKey.objects.create(
                        tenant_id=tenant_id,
                        key=idem_key,
                        response_status=102,
                        response_body={"message": "Processing request"}
                    )
                    record_id = record.id
            except IntegrityError:
                existing_record = IdempotencyKey.unscoped_objects.filter(tenant_id=tenant_id, key=idem_key).first()
                if existing_record and existing_record.response_status == 102:
                    return Response(
                        {"error": "Concurrent Lock: A duplicate request key is already active."},
                        status=status.HTTP_409_CONFLICT
                    )
                if existing_record:
                    return Response(existing_record.response_body, status=existing_record.response_status)
                return Response({"error": "Idempotency tracking conflict occurred."}, status=status.HTTP_409_CONFLICT)
            
            try:
                response = view_func(request, *args, **kwargs)
                
                if response.status_code < 500:
                    # Safely serialize out the response payload (handles UUIDs, datetimes, decimals)
                    if hasattr(response, 'data') and response.data is not None:
                        # Force DRF JSONRenderer to transform Python UUID objects to strings
                        rendered_content = JSONRenderer().render(response.data)
                        cleaned_body = json.loads(rendered_content)
                    else:
                        cleaned_body = {"message": str(response.content)}

                    IdempotencyKey.unscoped_objects.filter(id=record_id).update(
                        response_status=response.status_code,
                        response_body=cleaned_body  
                    )
                else:
                    IdempotencyKey.unscoped_objects.filter(id=record_id).delete()
                
                return response

            except Exception as e:
                if record_id:
                    IdempotencyKey.unscoped_objects.filter(id=record_id).delete()
                raise e
            
        return _wrapped_view
    return decorator