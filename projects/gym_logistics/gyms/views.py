
# from rest_framework import viewsets # type: ignore
# from .models import Branch, GymCompany, GymClass, Trainer
# from .serializers import GymCompanySerializer, GymClassSerializer, BranchSerializer, TrainerSerializer

# class GymCompanyViewSet(viewsets.ModelViewSet):
#     queryset = GymCompany.objects.all()
#     serializer_class = GymCompanySerializer

# class GymClassViewSet(viewsets.ModelViewSet):
#     queryset = GymClass.objects.all()
#     serializer_class = GymClassSerializer

# class TrainerviewSet(viewsets.ModelViewSet):
#     queryset = Trainer.objects.all()
#     serializer_class = TrainerSerializer

# class BranchViewSet(viewsets.ModelViewSet):
#     queryset = Branch.objects.all()
#     serializer_class = BranchSerializer


from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import GymCompany, Branch, Trainer, GymClass, ClassBooking, AttendanceLog, EquipmentAsset, TrainerSalary, Member
from .serializers import (
    GymCompanySerializer, GymClassSerializer, BranchSerializer, TrainerSerializer,
    TrainerSalarySerializer, ClassBookingSerializer, AttendanceLogSerializer, EquipmentAssetSerializer, MemberSerializer
)

# This class reads or adds to entire collection
class GymCompanyListCreateAPIView(APIView):
    serializer_class = GymCompanySerializer
    # GET : Feathc All the Gym Company
    def get(self, request): # When user open a page then it trigger this function.
        companies = GymCompany.objects.all() # grab every single row from GymCompany DB, save it in companies variable.
        serializer = GymCompanySerializer(companies, many=True) # pass the DB into serializer(translator), many=True means i proive you whole list, loop through them.
        return Response(serializer.data, status = status.HTTP_200_OK)

    # POST : Create a brand new Gym Company
    def post(self, request):
        serializer = GymCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class GymCompanyDetailAPIView(APIView):
    
    def get(self, request, pk):
        company = get_object_or_404(GymCompany, pk=pk)
        serializer = GymCompanySerializer(company) # We only targetting single row into JSON data.
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # PUT : Replace this whole record completely
    def put(self, request, pk):
        company = get_object_or_404(GymCompany,pk=pk) # if the row present point there or show Error 404
        serializer = GymCompanySerializer(company, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # PATCH : Partially update specific fields | Modify only these specific fields;
    def patch(self,request,pk):
        company = get_object_or_404(GymCompany, pk=pk)
        # Only Difference is partial = True means if the client sent one field like change email, don't mark missing fields as validation erros.
        seralizer = GymCompanySerializer(company, data = request.data, partial=True)
        
        if seralizer.is_valid():
            seralizer.save()
            return Response(seralizer.data, status=status.HTTP_200_OK)
        return Response(seralizer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # DELETE : Wipe a company row from the database
    def delete(self,request,pk):
        # Grabs the row targeted for deletion.
        company = get_object_or_404(GymCompany, pk=pk)
        company.delete() # SQL DELETE querey to drops this row from database.
        return Response(
            {"Message":" Company Deleted Successfully"},
            status = status.HTTP_204_NO_CONTENT
        )


                    ## === Branch Views Custom API === ##

class BranchListCreateAPIView(APIView):
    def get(self, request):
        branches = Branch.objects.all()
        serailizer = BranchSerializer(branches, many=True)
        return Response(serailizer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BranchDetailAPIView(APIView):
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        serializer = BranchSerializer(branch)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
                # === TRAINER MANUAL Custom API VIEWS ===
class TrainerListCreateAPIView(APIView):
    def get(self, request):
        trainers = Trainer.objects.all()
        serializer = TrainerSerializer(trainers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TrainerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrainerDetailAPIView(APIView):
    def get(self, request, pk):
        trainer = get_object_or_404(Trainer, pk=pk)
        serializer = TrainerSerializer(trainer)
        return Response(serializer.data, status=status.HTTP_200_OK)


                # === GYM CLASS Custom API MANUAL VIEWS ===
class GymClassListCreateAPIView(APIView):
    def get(self, request):
        classes = GymClass.objects.all()
        serializer = GymClassSerializer(classes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GymClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GymClassDetailAPIView(APIView):
    def get(self, request, pk):
        gym_class = get_object_or_404(GymClass, pk=pk)
        serializer = GymClassSerializer(gym_class)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class TrainerSalaryAPIView(APIView):
    def get(self, request, trainer_id):
        salary = get_object_or_404(TrainerSalary, trainer_id=trainer_id)
        
        # Security Checking
        corporate_auth_header = request.headers.get('X-Corporate-ID')
        
        if not corporate_auth_header or int(corporate_auth_header) != salary.gym_company.id:
            return Response(
                {"Error": "Security Breach: Unauthorized organization configuration access requested."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = TrainerSalarySerializer(salary)
        return Response(serializer.data, status = status.HTTP_200_OK)
        
class ClassBookingCreateAPIView(APIView):
    def post(self, request):
        member_id = request.data.get('member')
        target_class_id = request.data.get('gym_class')
        
        target_class = get_object_or_404(GymClass, id=target_class_id)
        member_profile = get_object_or_404(Member, id=member_id)
        
        existing_bookings = ClassBooking.objects.filter(
            member = member_profile,
            gym_class__day_of_week = target_class.day_of_week
        )
        
        for booking in existing_bookings:
            current_scheduled_class = booking.gym_class
            
            if target_class.start_time < current_scheduled_class.end_time and target_class.end_time > current_scheduled_class.start_time:
                return Response({
                    "Validation_Failure": "Schedule Collision!",
                    "Details": f"Cannot register for '{target_class.name}'. Time conflicts with your existing reservation: '{current_scheduled_class.name}' at {current_scheduled_class.branch.name}."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ClassBookingSerializer(data=request.data)
        if serializer.is_valid():
            new_booking = serializer.save()
            
            # AUTOMATION FEATURE: Automatically log attendance as 'PRESENT' upon registration
            AttendanceLog.objects.create(booking=new_booking, status='PRESENT')
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AttendanceStatusToggleAPIView(APIView):
    def patch(self,request, log_id):
        log = get_object_or_404(AttendanceLog, id=log_id)
        new_status = request.data.get('status')
        
        if new_status not in ['PRESENT','ABSENT']:
            return Response({"Error" : "Invalide status option submitted"}, status = status.HTTP_400_BAD_REQUEST)
        log.status = new_status
        log.save()
        
        return Response({
            "Success": f"Attendance status successfully updated to {new_status} for {log.booking.member}."
        }, status=status.HTTP_200_OK)
        
        
class EquipmentBranchInventoryAPIView(APIView):
    def get(self, request, branch_id):
        assets = EquipmentAsset.objects.filter(branch_id=branch_id)
        serializer = EquipmentAssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, branch_id):
        data = request.data.copy()
        data['branch'] = branch_id
        
        serializer = EquipmentAssetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class MemberListCreateAPIView(APIView):
    def get(self, request):
        members = Member.objects.all()
        serializer = MemberSerializer(members, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = MemberSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)
    
class MemberDetailAPIView(APIView):
    def get(self,request,pk):
        member = get_object_or_404(Member,pk=pk)
        serializer = MemberSerializer(member)
        return Response(serializer.data,status=status.HTTP_200_OK)
        