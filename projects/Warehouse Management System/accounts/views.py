from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationsSerializer
from .services.user_service import UserServices

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def register(self, request):
        serializer = UserRegistrationsSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user_instance = UserServices.register_new_user(serializer.validated_data)
        
        return Response({
            "status":"User Successfully created",
            "user":{
                "id":user_instance.id,
                "email":user_instance.email,
                "role":user_instance.role 
            }
        }, status = status.HTTP_201_CREATED)