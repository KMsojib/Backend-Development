from django.db import models

# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_email = models.EmailField(unique=True)
    company_req_number = models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return self.name
    
class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location_city = models.CharField(max_length=100)
    max_cubic_meters_capacity = models.PositiveBigIntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.location_city})"
    
    
class InventoryItem(models.Model):
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=255,unique=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="inventory_items"
    )
    
    def __str__(self):
        return f"{self.title} [SKU: {self.sku}]"
    
class StockLevel(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="stock_levels"
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name = "stock_levels"
    )
    quantity = models.PositiveBigIntegerField(default=0)
    low_stock_threshold = models.PositiveBigIntegerField(default=10)
    
    class Meta:
        unique_together = ['warehouse','inventory_item']
    
    def __str__(self):
        return f"{self.inventory_item.title} in {self.warehouse.name}: Qty {self.quantity}"

class StockMovementLog(models.Model):
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name="movement_logs"
    )
    
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="outgoing_logs"
    )
    
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT, 
        related_name="incoming_logs"
    )
    
    quantity_moved = models.PositiveBigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Moved {self.quantity_moved} x {self.inventory_item.sku} at {self.timestamp}"