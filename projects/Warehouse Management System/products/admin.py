from django.contrib import admin
from .models import Category, Product, StockMovement

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'price', 'stock', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku')

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'movement_type', 'quantity', 'performed_by', 'created_at')
    list_filter = ('movement_type',)
    
    # Stock logs shouldn't be manually editable by people inside admin panel!
    readonly_fields = ('product', 'movement_type', 'quantity', 'performed_by', 'created_at')