
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

from .models import GymCompany,Branch,Trainer,GymClass
from .serializers import GymCompanySerializer, GymClassSerializer, BranchSerializer, TrainerSerializer
                    
                    # === GYM COMPANY MANUAL VIEWS ===
# This class reads or adds to entire collection
class GymCompanyListCreateAPIView(APIView):
    
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


                    ## === Branch Manual Views === ##

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
    
    
    # === TRAINER MANUAL VIEWS ===
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


# === GYM CLASS MANUAL VIEWS ===
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