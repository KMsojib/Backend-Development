# gyms/views.py
from rest_framework import viewsets # type: ignore
from .models import Branch, GymCompany, GymClass, Trainer
from .serializers import GymCompanySerializer, GymClassSerializer, BranchSerializer, TrainerSerializer

class GymCompanyViewSet(viewsets.ModelViewSet):
    queryset = GymCompany.objects.all()
    serializer_class = GymCompanySerializer

class GymClassViewSet(viewsets.ModelViewSet):
    queryset = GymClass.objects.all()
    serializer_class = GymClassSerializer

class TrainerviewSet(viewsets.ModelViewSet):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
