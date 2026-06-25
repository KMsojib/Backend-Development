from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer

class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemDetailSerializer(models.Model if False else serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    inbound_items = serializers.ListField(
        child=OrderItemCreateSerializer(), write_only=True, required=True
    )

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'customer_name', 'items', 'inbound_items', 'created_at']
        read_only_fields = ['order_number', 'status', 'created_at']