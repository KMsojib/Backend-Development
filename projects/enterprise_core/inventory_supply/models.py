from django.db import models
from django.core.exceptions import ValidationError

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    
    def __str__(self):
        return self.name
    

class StockItem(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    current_stock = models.IntegerField(default=0)
    minimum_required = models.IntegerField(default=5)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
class WastageLog(models.Model):
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    quantity_lost = models.IntegerField()
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.quantity_lost > self.stock_item.current_stock:
            raise ValidationError("Cannot record more wastage than what is currently in stock.")