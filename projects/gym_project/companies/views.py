from django.shortcuts import render
from rest_framework.views import APIView #type:ignore
import companies
from rest_framework import viewsets #type: ignore
from rest_framework import status #type: ignore
from rest_framework.response import Response #type: ignore
from .models import GymCompany, Branch
from .serializers import GymCompanySerializer, BranchSerializer

class GymCompanyListCreateAPIView(APIView):
    def get(self, request):
        companies = GymCompany.objects.all()
        serializer = GymCompanySerializer(companies, many =True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = GymCompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BranchListCreateAPIView(APIView):
    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    