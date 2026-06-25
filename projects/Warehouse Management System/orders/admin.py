from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'status', 'customer_name', 'created_at')
    list_filter = ('status',)
    search_fields = ('order_number', 'customer_name')
    inlines = [OrderItemInline]