import uuid
from django.db import models
from .managers import TenantScopedManager

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
    unscoped_objects = models.Manager() 

    class Meta:
        abstract = True


class Wallet(TenantScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100) 

    class Meta:
        unique_together = ('tenant', 'user_id')

    def __str__(self):
        return f"{self.user_id} (Tenant: {self.tenant.name})"
    @property
    def balance(self):
        aggregates = self.transactions.aggregate(total=models.Sum('amount'))
        return aggregates['total'] or 0


class Transaction(TenantScopedModel):
    TRANSACTION_TYPES = (
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('TRANSFER', 'Transfer'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.IntegerField() 
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference_id = models.UUIDField(null=True, blank=True) 

    class Meta:
        ordering = ['-created_at']


class IdempotencyKey(TenantScopedModel):
    key = models.CharField(max_length=255)
    response_status = models.IntegerField()
    response_body = models.JSONField()

    class Meta:
        unique_together = ('tenant', 'key') 