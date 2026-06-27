from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore
from django.core.exceptions import ValidationError
from .serializers import ClassBookingSerializer
from .services import GymBookingEngine

class ClassBookingCreateAPIView(APIView):
    def post(self,request):
        member_id = request.data.get('member')
        gym_class_id = request.data.get('gym_class')
        
        if not member_id or not gym_class_id:
            return Response(
                {"error":"Missing inputs, Required Body Parameter Member and Gym Class"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            new_booking = GymBookingEngine.deploy_booking_safeguard(
                member_id=int(member_id),
                gym_class_id=int(gym_class_id)
            )
            
            serializer = ClassBookingSerializer(new_booking)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValidationError as error:
            return Response({"validation_error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as unexpected_error:
            return Response({"error": "Processing system failure"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)