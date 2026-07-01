from rest_framework import viewsets, status #type:ignore
from rest_framework.decorators import action #type:ignore
from rest_framework.response import Response #type:ignore
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator

from .models import Tenant, Wallet, Transaction
from .serializers import (
    TenantSerializer, WalletSerializer, TransactionSerializer,
    DepositWithdrawSerializer, TransferSerializer
)
from .services import WalletService
from .idempotency import idempotent_endpoint

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    # Overrides default query scoping since Tenant creation is global
    permission_classes = [] 


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer

    def get_queryset(self):
        # Automatically scoped by our custom TenantScopedManager
        return Wallet.objects.all()

    def perform_create(self, serializer):
        # Assign the tenant from the middleware context safely
        serializer.save(tenant_id=self.request.tenant_id)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Returns paginated transaction history for a specific wallet."""
        wallet = self.get_object()
        # Enforce scoping explicitly at the ledger boundary
        queryset = Transaction.objects.filter(wallet=wallet)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @method_decorator(idempotent_endpoint())
    def deposit(self, request, pk=None):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            tx = WalletService.deposit(
                tenant_id=request.tenant_id,
                wallet_id=pk,
                amount_minor_units=serializer.validated_data['amount']
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @method_decorator(idempotent_endpoint())
    def withdraw(self, request, pk=None):
        serializer = DepositWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            tx = WalletService.withdraw(
                tenant_id=request.tenant_id,
                wallet_id=pk,
                amount_minor_units=serializer.validated_data['amount']
            )
            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @method_decorator(idempotent_endpoint())
    def transfer(self, request, pk=None):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            sender_tx, receiver_tx = WalletService.transfer(
                tenant_id=request.tenant_id,
                from_wallet_id=pk,
                to_wallet_id=serializer.validated_data['to_wallet_id'],
                amount_minor_units=serializer.validated_data['amount']
            )
            return Response({
                "message": "Transfer successful",
                "sender_transaction": TransactionSerializer(sender_tx).data,
                "receiver_transaction": TransactionSerializer(receiver_tx).data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)