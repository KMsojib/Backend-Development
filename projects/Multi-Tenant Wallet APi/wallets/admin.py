from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Tenant, Wallet, Transaction, IdempotencyKey

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'id', 'balance', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('user_id',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'wallet', 'amount', 'type', 'created_at')
    list_filter = ('tenant', 'type')
    
    def save_model(self, request, obj, form, change):
        if not change:
            if obj.type == 'WITHDRAW' and obj.amount > 0:
                obj.amount = -obj.amount
            
            current_balance = obj.wallet.balance
            if obj.type == 'WITHDRAW' and (current_balance + obj.amount) < 0:
                raise ValidationError(f"Insufficient funds! Wallet only has {current_balance} cents.")
    

@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'tenant', 'response_status', 'created_at')
    list_filter = ('tenant',)