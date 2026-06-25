from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer
from .services.order_service import OrderService

class OrderViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order_instance = OrderService.create_pending_order(serializer.validated_data, request.user)
            output = OrderSerializer(order_instance)
            return Response(output.data, status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return Response({"error": error.message_dict}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        # prefetch_related handles nested relational item lookups efficiently
        queryset = Order.objects.prefetch_related('items__product__category').all()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        queryset = Order.objects.prefetch_related('items__product__category').all()
        order_instance = get_object_or_404(queryset, pk=pk)
        serializer = OrderSerializer(order_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def approve(self, request, pk=None):
        try:
            order_instance = OrderService.approve_and_deduct_stock(pk, request.user)
            return Response({"status": f"Order allocation approved. Status: {order_instance.status}."}, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def cancel(self, request, pk=None):
        try:
            order_instance = OrderService.cancel_order_workflow(pk, request.user)
            return Response({"status": f"Order status moved to CANCELLED. Inventory levels updated."}, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def complete(self, request, pk=None):
        try:
            order_instance = OrderService.complete_order_workflow(pk)
            return Response({"status": f"Order marked COMPLETED. Process finalized."}, status=status.HTTP_200_OK)
        except ValidationError as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)