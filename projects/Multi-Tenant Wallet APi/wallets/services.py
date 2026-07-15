import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Wallet, Transaction
from django.db import models

class WalletService:
    @classmethod
    @transaction.atomic
    def deposit(cls,tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
        if amount_minor_units <= 0:
            raise ValidationError("Deposit amount must be positive minor unit(cents/paisa).")

        wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
        tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=wallet,
            amount=amount_minor_units,
            type='DEPOSIT'
        )
        return tx

    @classmethod
    @transaction.atomic
    def withdraw(cls,tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
        if amount_minor_units <= 0:
            raise ValidationError("Withdrawal amount must be a positive integer minor unit.")
        wallet = Wallet.objects.select_for_update().get(pk=wallet_id)
        if wallet.balance < amount_minor_units:
            raise ValidationError("Insufficient funds for withdrawal.")

        tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=wallet,
            amount=-amount_minor_units,
            type='WITHDRAW'
        )
        return tx
    
    @classmethod
    @transaction.atomic
    def transfer(cls, tenant_id: str, from_wallet_id: str, to_wallet_id: str, amount_minor_units: int):
        if amount_minor_units <= 0:
            raise ValidationError("Transfer amount must be positive.")
        
        from_id_str = str(from_wallet_id)
        to_id_str = str(to_wallet_id)
        
        if from_id_str == to_id_str:
            raise ValidationError("Cannot transfer funds to the same wallet account.")
        
        id_list = [from_id_str, to_id_str]
        id_list.sort()
        locked_wallets = Wallet.unscoped_objects.select_for_update().in_bulk(id_list)
        
        sender_key = uuid.UUID(from_wallet_id) if isinstance(from_wallet_id, str) else from_wallet_id
        receiver_key = uuid.UUID(to_wallet_id) if isinstance(to_wallet_id, str) else to_wallet_id
        
        sender_wallet = locked_wallets.get(sender_key)
        receiver_wallet = locked_wallets.get(receiver_key)
        
        if not sender_wallet or str(sender_wallet.tenant_id) != str(tenant_id):
            raise ValidationError("Sender wallet not found within organization boundary.")
            
        if not receiver_wallet or str(receiver_wallet.tenant_id) != str(tenant_id):
            raise ValidationError("Receiver wallet not found within organization boundary.")
        
        if sender_wallet.currency != receiver_wallet.currency:
            raise ValidationError(
                f"Currency mismatch error. Cannot route transaction from "
                f"{sender_wallet.currency} to {receiver_wallet.currency} without an FX converter engine."
            )

        sender_balance = Transaction.objects.filter(wallet=sender_wallet).aggregate(total=models.Sum('amount'))['total'] or 0
        if sender_balance < amount_minor_units:
            raise ValidationError("Insufficient balance to execute this ledger transfer.")

        transfer_reference_link = uuid.uuid4()
        sender_tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=sender_wallet,
            amount=-amount_minor_units,  
            type='TRANSFER_OUT',
            reference_id=transfer_reference_link
        )

        # Add to receiver
        receiver_tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=receiver_wallet,
            amount=amount_minor_units,   
            type='TRANSFER_IN',         
            reference_id=transfer_reference_link
        )
        
        return sender_tx, receiver_tx
