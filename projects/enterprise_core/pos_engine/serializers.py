from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderLineItem
from inventory_supply.models import StockItem

class OrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineItem
        fields = ['menu_item', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderLineItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'table', 'status', 'total_amount', 'items']
        read_only_fields = ['total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                stock_item = item_data['menu_item']
                qty = item_data['quantity']
                
                if stock_item.current_stock < qty:
                    raise serializers.ValidationError(f"Not enough stock for {stock_item.name}.")
                
                stock_item.current_stock -= qty
                stock_item.save()
                
                OrderLineItem.objects.create(order=order, **item_data)
        return order