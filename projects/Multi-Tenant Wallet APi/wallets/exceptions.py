class WalletError(Exception):
    default_message = "Wallet operation failed."
    code = "wallet_error"

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class InsufficientFundsError(WalletError):
    default_message = "Insufficient funds."
    code = "insufficient_funds"


class WalletNotFoundError(WalletError):
    default_message = "Wallet not found."
    code = "wallet_not_found"


class InvalidAmountError(WalletError):
    default_message = "Amount must be a positive integer expressed in minor units."
    code = "invalid_amount"


class SameWalletTransferError(WalletError):
    default_message = "Cannot transfer a wallet to itself."
    code = "same_wallet_transfer"


class WalletInactiveError(WalletError):
    default_message = "Wallet is inactive."
    code = "wallet_inactive"


ERROR_STATUS_MAP = {
    "insufficient_funds": 422,
    "wallet_not_found": 404,
    "cross_tenant_operation": 403,
    "invalid_amount": 400,
    "same_wallet_transfer": 400,
    "wallet_inactive": 422,
}