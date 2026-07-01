from rest_framework import serializers # type:ignore
from .models import Tenant, Wallet, Transaction

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name','is_active' 'created_at']
        read_only_fields = ['id','api_key','created_at']


class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.IntegerField(read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user_id', 'balance', 'created_at']
        read_only_fields = ["id", "balance", "created_at"]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'type', 'reference_id', 'created_at']
        read_only_fields = fields

class DepositWithdrawSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(max_length=255)
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )


class TransferSerializer(serializers.Serializer):
    to_wallet_id = serializers.UUIDField()
    amount = serializers.IntegerField(min_value=1)
    idempotency_key = serializers.CharField(max_length=255)
    description = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )