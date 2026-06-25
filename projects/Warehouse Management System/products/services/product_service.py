from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ..models import Product, StockMovement, Category

User = get_user_model()

class ProductService:
    
    @staticmethod
    @transaction.atomic
    def create_new_product(validated_data: dict, performing_user: User) -> Product: # type:ignore
        category_id = validated_data.pop('category_id')
        try:
            category_instance = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise ValidationError({"category_id": "The specified category record does not exist."})

        return Product.objects.create(
            category=category_instance,
            created_by=performing_user,
            **validated_data
        )

    @staticmethod
    @transaction.atomic
    def increase_warehouse_stock(product_id: int, quantity: int, performing_user: User) -> Product: # type:ignore
        product = Product.objects.select_for_update().get(id=product_id)
        
        product.stock += quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.IN,
            quantity=quantity,
            performed_by=performing_user
        )
        return product

    @staticmethod
    @transaction.atomic
    def decrease_warehouse_stock(product_id: int, quantity: int, performing_user: User) -> Product: # type:ignore
        product = Product.objects.select_for_update().get(id=product_id)
        
        if product.stock < quantity:
            raise ValidationError({"stock": f"Insufficient inventory allocations. Current stock: {product.stock}."})

        product.stock -= quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            movement_type=StockMovement.MovementType.OUT,
            quantity=quantity,
            performed_by=performing_user
        )
        return product