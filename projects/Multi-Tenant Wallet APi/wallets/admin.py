from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Tenant, Customer, Wallet, Transaction, IdempotencyKey
from django import forms
from .services import WalletService
from django.contrib import messages  

class WalletInline(admin.TabularInline):
    model = Wallet
    extra = 0
    fields = ('balance','currency', 'display_balance', 'created_at')
    readonly_fields = ('currency', 'display_balance', 'created_at')
    can_delete = False
    
    def display_balance(self, obj):
        return f"{obj.balance} cents/paisa"
    display_balance.short_description = "Live Calculated Balance"


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('id', 'reference_id', 'created_at')
    can_delete = False
    fields = ('id', 'type', 'amount', 'reference_id', 'created_at')


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'tenant', 'currency', 'display_balance', 'created_at')
    list_filter = ('tenant', 'currency')
    search_fields = ('customer__user__username',) 
    inlines = [TransactionInline]  
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "customer":
            kwargs["queryset"] = db_field.related_model.unscoped_objects.all()
        if db_field.name == "tenant":
            kwargs["queryset"] = db_field.related_model.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
   
    def get_queryset(self, request):
        return self.model.unscoped_objects.get_queryset()
    
    def display_balance(self, obj):
        return f"{obj.balance} units"
    display_balance.short_description = 'Live Balance'


class TransactionAdminForm(forms.ModelForm):
    to_wallet = forms.ModelChoiceField(
        queryset=Wallet.unscoped_objects.all(),
        required=False,
        label="Destination Wallte (Only for Transfer)",
        help_text="Select where the money goes if you choose Type:Transfer"
    )    
    
    class Meta:
        model = Transaction
        fields = '__all__'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    list_display = ('id', 'tenant', 'wallet', 'amount', 'type', 'created_at')
    list_filter = ('tenant', 'type')
    
    fields = [
        'tenant', 
        'wallet', 
        'amount', 
        'type', 
        'to_wallet',   
        'reference_id'
    ]
    
    def get_queryset(self, request):
        return self.model.unscoped_objects.get_queryset()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "wallet":
            kwargs["queryset"] = db_field.related_model.unscoped_objects.all()
        if db_field.name == "tenant":
            kwargs["queryset"] = db_field.related_model.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if change:
            raise ValidationError("Ledger entries are completely immutable and cannot be updated.")
        
        if obj.type == 'TRANSFER':
            to_wallet = form.cleaned_data.get('to_wallet')
            if not to_wallet:
                raise ValidationError("You Must Select Destination wallet")
            try:
                sender_tx, receiver_tx = WalletService.transfer(
                    tenant_id = obj.tenant_id,
                    from_wallet_id = obj.wallet.id,
                    to_wallet_id = to_wallet.id,
                    amount_minor_units = abs(obj.amount)
                )
                
                self.message_user(
                    request, 
                    f"Successfully transferred {abs(obj.amount)} units from {obj.wallet} to {to_wallet}!", 
                    level=messages.SUCCESS
                )
            except ValidationError as flag:
                raise ValidationError(f"Transfer Failed: {flag}")
            except Exception as flag:
                raise ValidationError(f"System Error: {str(flag)}")
        else:
            try:
                if obj.type == 'DEPOSIT':
                    WalletService.deposit(obj.tenant_id, obj.wallet.id, obj.amount)
                elif obj.type == 'WITHDRAW':
                    WalletService.withdraw(obj.tenant_id, obj.wallet.id, abs(obj.amount))
                
                self.message_user(request, f"Successfully processed {obj.type} via Admin.", level=messages.SUCCESS)
            except Exception as e:
                raise ValidationError(f"Transaction failed: {str(e)}")
    
    

@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'tenant', 'response_status', 'created_at')
    list_filter = ('tenant',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'tenant', 'email', 'is_active')
    list_filter = ('tenant', 'is_active')
    search_fields = ('user__username', 'email')

    inlines = [WalletInline]
    
    def get_queryset(self, request):
        return self.model.unscoped_objects.get_queryset()
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

