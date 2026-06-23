from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .models import Warehouse,InventoryItem,StockLevel,StockMovementLog


class InventoryTransferService:
    @staticmethod
    @transaction.atomic
    
    def exectue_transfer(from_warehouse_id,to_warehouse_id, inventory_item_id,qty_to_move):
        from_where = get_object_or_404(Warehouse,id=from_warehouse_id)
        to_where = get_object_or_404(Warehouse,id=to_warehouse_id)
        item = get_object_or_404(InventoryItem,id=inventory_item_id)
        
        # Row-Level Cooncurrency locking 
        try:
            source_stock = StockLevel.objects.select_for_update().get(
                warehouse = from_where,
                inventory_item = item
            )
        except StockLevel.DoesNotExist:
            raise ValidationError("Requested product is completely unavialbe at the origin warehosue.")
        
        # Assert Stock Sufficiency Check
        if source_stock.quantity < qty_to_move:
            raise ValidationError(
                f"Insufficient Stok profile, Aviailable : {source_stock.quantity},Requested: {qty_to_move}"
            )
        # Deduct from source node
        source_stock.quantity -= qty_to_move
        source_stock.save()
        
        # Credit to Destination Node
        dest_stock, created = StockLevel.objects.select_for_update().get_or_create(
            warehouse = to_where,
            inventory_item = item,
            defaults={'quantity':0}
        )
        
        dest_stock.quantity += qty_to_move
        dest_stock.save()
        
        # Audit Record Ledger Logging
        StockMovementLog.objects.create(
            inventory_item = item,
            from_warehouse = from_where,
            to_warehouse = to_where,
            quantity_moved = qty_to_move
        )
        return f"Successfully shifted {qty_to_move} Units"
        