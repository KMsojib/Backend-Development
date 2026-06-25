from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    """
    The parent manifest tracking overall purchase status and destination paths.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Processing'
        APPROVED = 'APPROVED', 'Approved by Manager'
        CANCELLED = 'CANCELLED', 'Cancelled/Aborted'
        COMPLETED = 'COMPLETED', 'Fulfilled & Closed'

    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    customer_name = models.CharField(max_length=255)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number} ({self.status})"


class OrderItem(models.Model):
    """
    Individual nested data rows mapping a product quantity allocation to a parent Order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} on {self.order.order_number}"