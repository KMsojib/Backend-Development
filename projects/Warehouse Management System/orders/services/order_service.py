import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ..models import Order, OrderItem
from products.models import Product, StockMovement

User = get_user_model()

class OrderService:

    @staticmethod
    @transaction.atomic
    def create_pending_order(validated_data: dict, performing_user: User) -> Order:# type:ignore
        """Generates a tracking manifest and registers line item requirements."""
        inbound_items = validated_data.pop('inbound_items')
        customer_name = validated_data.get('customer_name')

        # Generate a unique order tracking code
        generated_number = f"WMS-{uuid.uuid4().hex[:8].upper()}"

        order = Order.objects.create(
            order_number=generated_number,
            customer_name=customer_name,
            created_by=performing_user,
            status=Order.Status.PENDING
        )

        for item_data in inbound_items:
            try:
                product_instance = Product.objects.get(id=item_data['product_id'])
            except Product.DoesNotExist:
                raise ValidationError({"product_id": f"Product item #{item_data['product_id']} not found."})

            OrderItem.objects.create(
                order=order,
                product=product_instance,
                quantity=item_data['quantity'],
                unit_price=product_instance.price
            )
        return order

    @staticmethod
    @transaction.atomic
    def approve_and_deduct_stock(order_id: int, performing_user: User) -> Order:# type:ignore
        """
        Locks inventory rows, checks stock availability, reduces totals, 
        and updates the status to APPROVED.
        """
        order = Order.objects.select_for_update().get(id=order_id)
        
        if order.status != Order.Status.PENDING:
            raise ValidationError(f"Order cannot be approved from its current status: {order.status}.")

        # Deduct stock for each line item in the order
        for item in order.items.all():
            product = Product.objects.select_for_update().get(id=item.product.id)
            
            if product.stock < item.quantity:
                raise ValidationError(f"Insufficient stock for product '{product.name}'. Required: {item.quantity}, Available: {product.stock}.")
            
            product.stock -= item.quantity
            product.save()

            # Record the stock movement audit log row
            StockMovement.objects.create(
                product=product,
                movement_type=StockMovement.MovementType.OUT,
                quantity=item.quantity,
                performed_by=performing_user
            )

        order.status = Order.Status.APPROVED
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order_workflow(order_id: int, performing_user: User) -> Order: # type:ignore
        """
        Cancels the order. If it was already approved, it replenishes 
        the stock levels automatically.
        """
        order = Order.objects.select_for_update().get(id=order_id)
        
        if order.status in [Order.Status.CANCELLED, Order.Status.COMPLETED]:
            raise ValidationError(f"Closed orders cannot be changed to a CANCELLED state.")

        # Re-increment stock if the order was already approved
        if order.status == Order.Status.APPROVED:
            for item in order.items.all():
                product = Product.objects.select_for_update().get(id=item.product.id)
                product.stock += item.quantity
                product.save()

                StockMovement.objects.create(
                    product=product,
                    movement_type=StockMovement.MovementType.IN,
                    quantity=item.quantity,
                    performed_by=performing_user
                )

        order.status = Order.Status.CANCELLED
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def complete_order_workflow(order_id: int) -> Order: # type:ignore
        order = Order.objects.select_for_update().get(id=order_id)
        if order.status != Order.Status.APPROVED:
            raise ValidationError("Only approved warehouse distributions can transition to COMPLETED.")
        order.status = Order.Status.COMPLETED
        order.save()
        return order