from rest_framework import viewsets, status #type:ignore
from rest_framework.decorators import action #type:ignore
from rest_framework.response import Response #type:ignore
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator

from .models import Tenant, Customer, Wallet, Transaction, IdempotencyKey
from .serializers import (
    TenantSerializer, CustomerSerializer, WalletSerializer, TransactionSerializer,
    IdempotencyKeySerializer, DepositWithdrawSerializer, TransferSerializer
)
from .services import WalletService
from .idempotency import idempotent_endpoint
from rest_framework.pagination import PageNumberPagination #type:ignore

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [] 

class MasterAuditTimelinePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        show_all = self.request.query_params.get('all') == 'true'
        if show_all:
            return Customer.unscoped_objects.all()
        return Customer.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.tenant_id)

# Get overall history of each user or customer
    @action(detail = True, methods=['get'],url_path='overall-history')
    def overall_history(self,request,pk=None):
        show_all = request.query_params.get('all') == 'true'
        
        try:
            if show_all:
                # Bypasses EVERY single manager filter by hitting Django's core base manager
                customer = self.get_queryset().model._base_manager.get(pk=pk)
                wallets = Wallet.unscoped_objects.filter(customer=customer)
                queryset = Transaction.unscoped_objects.filter(wallet__in=wallets).order_by('-created_at')
            else:
                customer = self.get_object()
                wallets = Wallet.objects.filter(customer=customer)
                queryset = Transaction.objects.filter(wallet__in=wallets).order_by('-created_at')
        except Exception:
            return Response(
                {"error": f"ID {pk} was not found in the Customer database table. Double check that this is a Customer ID, not a Wallet ID!"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        # 2. Extract profile identities and current wallet properties
        customer_data = CustomerSerializer(customer).data
        wallet_data = WalletSerializer(wallets, many=True).data

        # 3. Fragment transaction streams via master page offsets
        paginator = MasterAuditTimelinePagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        
        if page is not None:
            tx_serializer = TransactionSerializer(page, many=True)
            response = paginator.get_paginated_response(tx_serializer.data)
            
            # Inject master context structural metadata
            response.data['customer'] = customer_data
            response.data['wallets'] = wallet_data
            return response

        # Non-paginated fallback structure
        tx_serializer = TransactionSerializer(queryset, many=True)
        return Response({
            "customer": customer_data,
            "wallets": wallet_data,
            "results": tx_serializer.data
        })
        
class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer

    def get_queryset(self):
        show_all = self.request.query_params.get('all') == 'true'
        if show_all:
            return Wallet.unscoped_objects.all()
        return Wallet.objects.all()

    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.tenant_id)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Returns the wallet's live balance alongside its paginated transaction history."""
        show_all = request.query_params.get('all') == 'true'
        
        if show_all:
            wallet = Wallet.unscoped_objects.get(pk=pk)
            queryset = Transaction.unscoped_objects.filter(wallet=wallet).order_by('-created_at')
        else:
            wallet = self.get_object()
            queryset = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            response.data['wallet_id'] = wallet.id
            response.data['currency'] = wallet.currency
            response.data['live_balance'] = wallet.balance
            return response

        serializer = TransactionSerializer(queryset, many=True)
        return Response({
            "wallet_id": wallet.id,
            "currency": wallet.currency,
            "live_balance": wallet.balance,
            "results": serializer.data
        })

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
            return Response({"error": str(e.messages[0] if hasattr(e, 'messages') else e)}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"error": str(e.messages[0] if hasattr(e, 'messages') else e)}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"error": str(e.messages[0] if hasattr(e, 'messages') else e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        show_all = self.request.query_params.get('all') == 'true'
        if show_all:
            return Transaction.unscoped_objects.all()
        return Transaction.objects.all()


class IdempotencyKeyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IdempotencyKeySerializer

    def get_queryset(self):
        show_all = self.request.query_params.get('all') == 'true'
        if show_all:
            return IdempotencyKey.unscoped_objects.all()
        return IdempotencyKey.objects.all()