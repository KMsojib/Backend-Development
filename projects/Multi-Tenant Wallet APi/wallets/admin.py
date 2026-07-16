from django.contrib import admin,messages
from .models import Tenant, Customer, Wallet, Transaction, IdempotencyKey
from django import forms 
from .services import WalletService
from django.core.exceptions import ValidationError
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

class WalletTransferForm(forms.Form):
    to_wallet = forms.ModelChoiceField(
        queryset=Wallet.unscoped_objects.none(),
        label="Recipient Wallet",
        widget=forms.Select(attrs={'style': 'width: 300px; padding: 5px;'})
    )
    amount = forms.IntegerField(
        label="Amount (Minor Units)",
        min_value=1
    )

    def __init__(self, *args, **kwargs):
        # We pass the active sender_wallet into the form initialization
        sender_wallet = kwargs.pop('sender_wallet', None)
        super().__init__(*args, **kwargs)
        if sender_wallet:
            # 💡 Populate only with wallets sharing the SAME tenant and currency
            self.fields['to_wallet'].queryset = Wallet.unscoped_objects.filter(
                tenant_id=sender_wallet.tenant_id,
                currency=sender_wallet.currency
            ).exclude(id=sender_wallet.id)




class TransactionAdminForm(forms.ModelForm):
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=True,
        label="Tenant"
    )
    wallet = forms.ModelChoiceField(
        queryset=Wallet.unscoped_objects.all(),
        required=True,
        label="Source Wallet"
    )
    to_wallet = forms.ModelChoiceField(
        queryset=Wallet.unscoped_objects.all(),
        required=False,
        label="Recipient Wallet (For Transfers Only)",
        help_text="Select the destination wallet if executing a Transfer."
    )

    class Meta:
        model = Transaction
        fields = ['tenant', 'wallet', 'type', 'amount', 'to_wallet']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Ensure all choices default to unscoped pools so they aren't blank
        self.fields['tenant'].queryset = Tenant.objects.all()
        self.fields['wallet'].queryset = Wallet.unscoped_objects.all()
        self.fields['to_wallet'].queryset = Wallet.unscoped_objects.all()

        # Extract active tenant context if it exists
        t_id = None
        if self.instance and self.instance.pk and getattr(self.instance, 'tenant_id', None):
            t_id = self.instance.tenant_id
        elif self.request and getattr(self.request, 'tenant_id', None):
            t_id = self.request.tenant_id

        # If a tenant context is active, filter the options dynamically
        if t_id:
            self.fields['wallet'].queryset = Wallet.unscoped_objects.filter(tenant_id=t_id)
            self.fields['to_wallet'].queryset = Wallet.unscoped_objects.filter(tenant_id=t_id)

    def clean(self):
        cleaned_data = super().clean()
        selected_tenant = cleaned_data.get('tenant')
        wallet = cleaned_data.get('wallet')
        to_wallet = cleaned_data.get('to_wallet')
        tx_type = cleaned_data.get('type')
        amount = cleaned_data.get('amount')

        # Validation 1: Force positive amount entries
        if amount and amount <= 0:
            raise ValidationError({"amount": "Transaction amount must be a positive integer."})

        # Validation 2: Ensure source wallet belongs to selected Tenant
        if wallet and selected_tenant and wallet.tenant_id != selected_tenant.id:
            raise ValidationError({
                "wallet": f"Security Violation: Selected wallet belongs to tenant '{wallet.tenant.name}', "
                          f"not the chosen form tenant '{selected_tenant.name}'."
            })

        # Validation 3: Overdraft prevention for WITHDRAWALS
        if tx_type == 'WITHDRAW' and wallet and amount:
            if wallet.balance < amount:
                raise ValidationError({
                    "amount": f"Insufficient funds! '{wallet.customer.user.username}' only has {wallet.balance} units, "
                              f"cannot execute withdrawal of {amount} units."
                })

        # Validation 4: Safety & Overdraft checks for TRANSFERS
        if tx_type in ['TRANSFER_IN', 'TRANSFER_OUT']:
            if not to_wallet:
                raise ValidationError({"to_wallet": "A recipient wallet must be selected for transfers."})
            
            if to_wallet.tenant_id != selected_tenant.id:
                raise ValidationError({
                    "to_wallet": f"Security Violation: Recipient wallet belongs to tenant '{to_wallet.tenant.name}', "
                                 f"not the chosen form tenant '{selected_tenant.name}'."
                })

            if wallet == to_wallet:
                raise ValidationError({"to_wallet": "Cannot transfer funds to the same wallet account."})

            if wallet.currency != to_wallet.currency:
                raise ValidationError({"to_wallet": f"Currency mismatch! {wallet.currency} cannot go to {to_wallet.currency}."})

            if wallet and amount and wallet.balance < amount:
                raise ValidationError({
                    "amount": f"Insufficient balance for transfer. Available: {wallet.balance} units."
                })

        return cleaned_data


@admin.register(Transaction)
class TransactionAdmin(TenantScopedAdminBase):
    form = TransactionAdminForm
    list_display = ('id', 'tenant', 'wallet', 'type', 'amount_display', 'reference_id', 'created_at')
    list_filter = ('tenant', 'type', 'created_at')
    search_fields = ('wallet__id', 'reference_id')
    readonly_fields = ('created_at', 'reference_id')

    def amount_display(self, obj):
        return f"{obj.amount} units"
    amount_display.short_description = 'Amount'

    def get_form(self, request, obj=None, change=False, **kwargs):
        Form = super().get_form(request, obj, change, **kwargs)
        class RequestForm(Form):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
        return RequestForm

    def save_model(self, request, obj, form, change):
        positive_amount = abs(obj.amount)

        if obj.type == 'WITHDRAW':
            # Automatically save as a negative transaction record
            obj.amount = -positive_amount
            super().save_model(request, obj, form, change)

        elif obj.type == 'DEPOSIT':
            # Save as a positive transaction record
            obj.amount = positive_amount
            super().save_model(request, obj, form, change)

        elif obj.type in ['TRANSFER_OUT', 'TRANSFER_IN']:
            to_wallet = form.cleaned_data.get('to_wallet')
            try:
                # Direct both actions to run inside a safe transactional ledger block
                WalletService.transfer(
                    tenant_id=obj.tenant_id,
                    from_wallet_id=str(obj.wallet.id),
                    to_wallet_id=str(to_wallet.id),
                    amount_minor_units=positive_amount
                )
                self.message_user(request, "Atomic Transfer completed successfully!", level=messages.SUCCESS)
            except ValidationError as e:
                self.message_user(request, f"Transfer Failed: {str(e)}", level=messages.ERROR)