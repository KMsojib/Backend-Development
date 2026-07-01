from django.db import transaction
from django.core.exceptions import ValidationError
import uuid
from .models import Wallet, Transaction

class WalletService:
    @staticmethod
    @transaction.atomic
    def deposit(tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
        if amount_minor_units <= 0:
            raise ValidationError("Deposit amount must be greater than zero.")

        wallet = Wallet.objects.select_for_update().get(id=wallet_id, tenant_id=tenant_id)
        
        tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=wallet,
            amount=amount_minor_units,
            type='DEPOSIT'
        )
        return tx

    @staticmethod
    @transaction.atomic
    def withdraw(tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
        if amount_minor_units <= 0:
            raise ValidationError("Withdrawal amount must be greater than zero.")

        wallet = Wallet.objects.select_for_update().get(id=wallet_id, tenant_id=tenant_id)
        
        if wallet.balance < amount_minor_units:
            raise ValidationError("Insufficient funds.")


        tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=wallet,
            amount=-amount_minor_units,
            type='WITHDRAW'
        )
        return tx

    @staticmethod
    @transaction.atomic
    def transfer(tenant_id: str, from_wallet_id: str, to_wallet_id: str, amount_minor_units: int) -> tuple:
        if amount_minor_units <= 0:
            raise ValidationError("Transfer amount must be greater than zero.")
        
        if from_wallet_id == to_wallet_id:
            raise ValidationError("Cannot transfer funds to the same wallet.")

      
        wallet_ids = sorted([str(from_wallet_id), str(to_wallet_id)])
        
       
        wallets_dict = {
            str(w.id): w for w in Wallet.objects.select_for_update().filter(
                id__in=wallet_ids, tenant_id=tenant_id
            )
        }

        from_wallet = wallets_dict.get(str(from_wallet_id))
        to_wallet = wallets_dict.get(str(to_wallet_id))

        if not from_wallet or not to_wallet:
            raise ValidationError("One or both wallets do not exist under this tenant.")

        if from_wallet.balance < amount_minor_units:
            raise ValidationError("Insufficient funds for this transfer.")

        transfer_reference = uuid.uuid4()

        sender_tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=from_wallet,
            amount=-amount_minor_units,
            type='TRANSFER',
            reference_id=transfer_reference
        )

        receiver_tx = Transaction.objects.create(
            tenant_id=tenant_id,
            wallet=to_wallet,
            amount=amount_minor_units,
            type='TRANSFER',
            reference_id=transfer_reference
        )

        return sender_tx, receiver_tx