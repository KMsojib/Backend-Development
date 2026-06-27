from rest_framework import serializers
from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    brand_name = serializers.CharField(source='storefront.brand_name', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'user_name', 'storefront', 'brand_name']