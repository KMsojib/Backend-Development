from django.contrib import admin
from .models import Tenant, Customer, Wallet, Transaction, IdempotencyKey

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


class TenantScopedAdminBase(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.unscoped_objects.all()


@admin.register(Customer)
class CustomerAdmin(TenantScopedAdminBase):
    list_display = ('id', 'tenant', 'user', 'email', 'is_active', 'created_at')
    list_filter = ('tenant', 'is_active')
    search_fields = ('user__username', 'email')
    raw_id_fields = ('user',)  

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    can_delete = True
    readonly_fields = ('tenant', 'type', 'amount', 'reference_id', 'created_at')
    
    def had_add_permission(self, request, obj=None):
        return False

@admin.register(Wallet)
class WalletAdmin(TenantScopedAdminBase):
    list_display = ('id', 'tenant', 'customer', 'currency', 'current_balance', 'created_at')
    list_filter = ('tenant', 'currency')
    search_fields = ('customer__user__username', 'id')
    readonly_fields = ('current_balance',)

    inlines = [TransactionInline]
    
    def current_balance(self, obj):
        return obj.balance
    current_balance.short_description = 'Live Balance (Minor Units)'


@admin.register(Transaction)
class TransactionAdmin(TenantScopedAdminBase):
    list_display = ('id', 'tenant', 'wallet', 'type', 'amount_display', 'reference_id', 'created_at')
    list_filter = ('tenant', 'type', 'created_at')
    search_fields = ('wallet__id', 'reference_id')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request):
        return False
    
    def amount_display(self, obj):
        return f"{obj.amount} units"
    amount_display.short_description = 'Amount'


@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(TenantScopedAdminBase):
    list_display = ('key', 'tenant', 'response_status', 'created_at')
    list_filter = ('tenant', 'response_status')
    search_fields = ('key',)
    readonly_fields = ('created_at',)