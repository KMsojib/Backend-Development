from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'stock', 'category_id', 'category', 'is_active']
        read_only_fields = ['stock', 'is_active']

    def validate_sku(self, value):
        if Product.objects.filter(sku=value.upper()).exists():
            raise serializers.ValidationError("A product with this SKU code already exists inside the ledger.")
        return value.upper()


class StockAdjustmentSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)