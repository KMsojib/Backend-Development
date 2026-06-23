from django.contrib import admin
from .models import Supplier,Warehouse,InventoryItem,StockMovementLog,StockLevel


class StockLevelInline(admin.TabularInline):
    model = StockLevel
    extra = 2
    

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name','location_city','max_cubic_meters_capacity')
    inlines = [StockLevelInline]

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('title','sku','unit_cost','supplier')
    search_fields = ('title','sku',)
    list_filter = ['supplier']
    
@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'warehouse', 'quantity', 'low_stock_threshold', 'check_status')
    list_filter = ['warehouse', 'inventory_item',]
    
    # Custom Computed Metric Field
    def check_status(self, obj):
        if obj.quantity <= obj.low_stock_threshold:
            return "LOW STOCK"
        return "Healthy"
    check_status.short_description = 'Status Alert'
    
    
@admin.register(StockMovementLog)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('inventory_item','from_warehouse','to_warehouse','quantity_moved', 'timestamp')
    readonly_fields = ('inventory_item', 'from_warehouse', 'to_warehouse', 'quantity_moved', 'timestamp')
    
admin.site.register(Supplier)