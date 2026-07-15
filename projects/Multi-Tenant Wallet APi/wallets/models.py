import uuid
from django.db import models
from django.contrib.auth.models import User 
from .managers import TenantScopedManager,UnscopedManager

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TenantScopedModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()
    unscoped_objects = UnscopedManager()

    class Meta:
        abstract = True
        base_manager_name = 'unscoped_objects'


class Customer(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='customer_profiles')
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tenant', 'user')

    def __str__(self):
        return f"{self.user.username} ({self.tenant.name})"


class Wallet(TenantScopedModel):
    CURRENCY_CHOICES = (
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('BDT', 'Bangladeshi Taka'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='wallets') # <--- Added
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')       # <--- Added

    class Meta:
        unique_together = ('tenant', 'customer', 'currency')

    @property
    def balance(self):
        aggregates = self.transactions.aggregate(total=models.Sum('amount'))
        return aggregates['total'] or 0

    def __str__(self):
        return f"{self.customer.user.username}'s Wallet ({self.currency})"


class Transaction(TenantScopedModel):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdrawal'),
        ('TRANSFER_IN', 'Transfer In'), 
        ('TRANSFER_OUT', 'Transfer Out'), 
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.IntegerField()
    type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    reference_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"[{self.type}] {self.amount} Minor Units -> {self.wallet.id}"

class IdempotencyKey(TenantScopedModel):
    key = models.CharField(max_length=255)
    response_status = models.IntegerField()
    response_body = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'key')
        
    def __str__(self):
        return f"Idempotency Key: {self.key} [{self.response_status}]"