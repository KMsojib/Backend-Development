from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from .models import AuditLog
from rest_framework.serializers import ModelSerializer

class AuditLogSerializer(ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = AuditLog
        fields = ['id', 'user_email', 'action', 'content_type', 'object_id', 'created_at']

class AuditLogViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = AuditLog.objects.select_related('user').order_by('-created_at')
        serializer = AuditLogSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)