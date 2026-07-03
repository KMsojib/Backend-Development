# from django.db import transaction
# from django.core.exceptions import ValidationError
# import uuid
# from .models import Wallet, Transaction

# class WalletService:
#     @staticmethod
#     @transaction.atomic
#     def deposit(tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
#         if amount_minor_units <= 0:
#             raise ValidationError("Deposit amount must be greater than zero.")

#         wallet = Wallet.objects.select_for_update().get(id=wallet_id, tenant_id=tenant_id)
        
#         tx = Transaction.objects.create(
#             tenant_id=tenant_id,
#             wallet=wallet,
#             amount=amount_minor_units,
#             type='DEPOSIT'
#         )
#         return tx

#     @staticmethod
#     @transaction.atomic
#     def withdraw(tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
#         if amount_minor_units <= 0:
#             raise ValidationError("Withdrawal amount must be greater than zero.")

#         wallet = Wallet.objects.select_for_update().get(id=wallet_id, tenant_id=tenant_id)
        
#         if wallet.balance < amount_minor_units:
#             raise ValidationError("Insufficient funds.")


#         tx = Transaction.objects.create(
#             tenant_id=tenant_id,
#             wallet=wallet,
#             amount=-amount_minor_units,
#             type='WITHDRAW'
#         )
#         return tx

#     @staticmethod
#     @transaction.atomic
#     def transfer(tenant_id: str, from_wallet_id: str, to_wallet_id: str, amount_minor_units: int) -> tuple:
#         if amount_minor_units <= 0:
#             raise ValidationError("Transfer amount must be greater than zero.")
        
#         if from_wallet_id == to_wallet_id:
#             raise ValidationError("Cannot transfer funds to the same wallet.")

      
#         wallet_ids = sorted([str(from_wallet_id), str(to_wallet_id)])
        
       
#         wallets_dict = {
#             str(w.id): w for w in Wallet.objects.select_for_update().filter(
#                 id__in=wallet_ids, tenant_id=tenant_id
#             )
#         }

#         from_wallet = wallets_dict.get(str(from_wallet_id))
#         to_wallet = wallets_dict.get(str(to_wallet_id))

#         if not from_wallet or not to_wallet:
#             raise ValidationError("One or both wallets do not exist under this tenant.")

#         if from_wallet.balance < amount_minor_units:
#             raise ValidationError("Insufficient funds for this transfer.")

#         transfer_reference = uuid.uuid4()

#         sender_tx = Transaction.objects.create(
#             tenant_id=tenant_id,
#             wallet=from_wallet,
#             amount=-amount_minor_units,
#             type='TRANSFER',
#             reference_id=transfer_reference
#         )

#         receiver_tx = Transaction.objects.create(
#             tenant_id=tenant_id,
#             wallet=to_wallet,
#             amount=amount_minor_units,
#             type='TRANSFER',
#             reference_id=transfer_reference
#         )

#         return sender_tx, receiver_tx


# wallets/services.py
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Wallet, Transaction

class WalletService:

    @staticmethod
    def deposit(tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
        """Atomically locks the wallet and credits funds."""
        if amount_minor_units <= 0:
            raise ValidationError("Deposit amount must be positive.")

        with transaction.atomic():
            # select_for_update locks this database row so no other request can touch it simultaneously
            wallet = Wallet.unscoped_objects.select_for_update().get(id=wallet_id, tenant_id=tenant_id)
            
            tx = Transaction.objects.create(
                tenant_id=tenant_id,
                wallet=wallet,
                amount=amount_minor_units,
                type='DEPOSIT'
            )
            return tx

    @staticmethod
    def withdraw(tenant_id: str, wallet_id: str, amount_minor_units: int) -> Transaction:
        """Atomically checks balance locks and debits funds."""
        if amount_minor_units <= 0:
            raise ValidationError("Withdrawal amount must be positive.")

        with transaction.atomic():
            wallet = Wallet.unscoped_objects.select_for_update().get(id=wallet_id, tenant_id=tenant_id)
            
            # Use the live balance safety metric we established
            if wallet.balance < amount_minor_units:
                raise ValidationError("Insufficient funds for withdrawal.")

            tx = Transaction.objects.create(
                tenant_id=tenant_id,
                wallet=wallet,
                # Withdrawals are kept as negative values inside the transaction table matrix
                amount=-amount_minor_units,
                type='WITHDRAW'
            )
            return tx

    @staticmethod
    def transfer(tenant_id: str, from_wallet_id: str, to_wallet_id: str, amount_minor_units: int):
        """Executes a multi-currency validation cross-ledger atomic transfer."""
        if from_wallet_id == to_wallet_id:
            raise ValidationError("Cannot transfer funds to the same wallet account.")
        if amount_minor_units <= 0:
            raise ValidationError("Transfer amount must be positive.")

        with transaction.atomic():
            # Fetch and lock both rows up front to avoid deadlocks
            sender_wallet = Wallet.unscoped_objects.select_for_update().get(id=from_wallet_id, tenant_id=tenant_id)
            receiver_wallet = Wallet.unscoped_objects.select_for_update().get(id=to_wallet_id, tenant_id=tenant_id)

            # REAL-WORLD CRITICAL GUARD: Prevent cross-currency mixing!
            if sender_wallet.currency != receiver_wallet.currency:
                raise ValidationError(
                    f"Currency mismatch error. Cannot route transaction from "
                    f"{sender_wallet.currency} to {receiver_wallet.currency} without an FX rate converter engine."
                )

            # Balance Guard check
            if sender_wallet.balance < amount_minor_units:
                raise ValidationError("Insufficient balance to execute this ledger transfer.")

            # Generate distinct audit tracking reference ID for ledger transparency
            import uuid
            transfer_reference_link = uuid.uuid4()

            sender_tx = Transaction.objects.create(
                tenant_id=tenant_id,
                wallet=sender_wallet,
                amount=-amount_minor_units,
                type='TRANSFER',
                reference_id=transfer_reference_link
            )

            receiver_tx = Transaction.objects.create(
                tenant_id=tenant_id,
                wallet=receiver_wallet,
                amount=amount_minor_units,
                type='TRANSFER',
                reference_id=transfer_reference_link
            )

            return sender_tx, receiver_tx