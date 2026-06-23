from rest_framework import serializers
from .models import Warehouse, InventoryItem, StockLevel, Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class InventoryItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id','title','sku','unit_cost']
        
class StockLevelReadSerializer(serializers.ModelSerializer):
    inventory_item = InventoryItemDetailSerializer(read_only = True)
    status_alert = serializers.SerializerMethodField()
    
    class Meta:
        model = StockLevel
        fields = ['inventory_item', 'quantity', 'low_stock_threshold', 'status_alert']
    
    def get_status_alert(self,obj):
        if obj.quantity <= obj.low_stock_threshold:
            return "LOW_STOCK"
        return "HEALTHY"
    
class WarehouseInventorySerializer(serializers.ModelSerializer):
    stock_levels = StockLevelReadSerializer(many = True, read_only = True)
    class Meta:
        model = Warehouse
        fields = ['id','name','location_city','max_cubic_meters_capacity','stock_levels']
        
class InventoryTransferInputSerializer(serializers.Serializer):
    from_warehouse_id = serializers.IntegerField()
    to_warehouse_id = serializers.IntegerField()
    inventory_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Transfer volume parameter must be greater than zero.")
        return value

    def validate(self, data):
        if data['from_warehouse_id'] == data['to_warehouse_id']:
            raise serializers.ValidationError(
                {"destination_error": "Origin and destination distribution hubs cannot match."}
            )
        return data
            
    
    