from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import ProductSerializer, StockAdjustmentSerializer
from .services.product_service import ProductService

class ProductViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product = ProductService.create_new_product(serializer.validated_data, request.user)
            output = ProductSerializer(product)
            return Response(output.data, status=status.HTTP_201_CREATED)
        except ValidationError as err:
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = Product.objects.select_related('category').filter(is_active=True)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        queryset = Product.objects.select_related('category').all()
        product = get_object_or_404(queryset, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='add-stock')
    def add_stock(self, request, pk=None):
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = ProductService.increase_warehouse_stock(pk, serializer.validated_data['quantity'], request.user)
        return Response({"status": "Stock incremented successfully.", "current_stock": product.stock}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-stock')
    def remove_stock(self, request, pk=None):
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            product = ProductService.decrease_warehouse_stock(pk, serializer.validated_data['quantity'], request.user)
            return Response({"status": "Stock decremented successfully.", "current_stock": product.stock}, status=status.HTTP_200_OK)
        except ValidationError as err:
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)