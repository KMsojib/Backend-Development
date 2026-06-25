from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product, StockMovement
from orders.models import Order
from .models import AuditLog

@receiver(post_save, sender=Product)
def trace_product_mutations(sender, instance, created, **kwargs):
    action_text = "Product Record Created" if created else "Product Parameters Modified"
    AuditLog.objects.create(
        user=instance.created_by,
        action=f"{action_text}: {instance.name} (SKU: {instance.sku})",
        content_type="Product",
        object_id=instance.id
    )

@receiver(post_save, sender=StockMovement)
def trace_stock_adjustments(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.performed_by,
            action=f"Stock Level Adjustment ({instance.movement_type}) | Qty: {instance.quantity} on SKU: {instance.product.sku}",
            content_type="StockMovement",
            object_id=instance.id
        )

@receiver(post_save, sender=Order)
def trace_order_lifecycle_mutations(sender, instance, created, **kwargs):
    action_text = f"Order Manifest Initialized (Status: {instance.status})" if created else f"Order Lifecycle Updated to State: {instance.status}"
    AuditLog.objects.create(
        user=instance.created_by,
        action=f"{action_text} | Tracker Number: {instance.order_number}",
        content_type="Order",
        object_id=instance.id
    )