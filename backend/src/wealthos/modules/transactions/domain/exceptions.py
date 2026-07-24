"""Domain errors for the transactions module."""


class TransactionError(Exception):
    """Base domain error for transactions."""


class TransactionDescriptionEmpty(TransactionError):
    """Raised when a transaction description is blank or too short."""


class TransactionDescriptionTooLong(TransactionError):
    """Raised when a transaction description exceeds the allowed length."""


class InvalidTransactionType(TransactionError):
    """Raised when a transaction type is not supported."""


class InvalidTransactionStatus(TransactionError):
    """Raised when a transaction status is not supported."""


class ZeroEntryAmount(TransactionError):
    """Raised when a transaction entry has a zero amount."""


class TransactionNotFoundError(TransactionError):
    """Raised when the transaction cannot be found in the organization."""


class TransactionAlreadyVoided(TransactionError):
    """Raised when voiding an already voided transaction."""


class AccountNotFoundError(TransactionError):
    """Raised when a referenced account is missing in the organization."""


class AccountInactive(TransactionError):
    """Raised when posting against an archived account."""


class CategoryNotFoundError(TransactionError):
    """Raised when a referenced category is missing in the organization."""


class CategoryInactive(TransactionError):
    """Raised when posting against an inactive category."""


class TransactionCategoryTypeMismatch(TransactionError):
    """Raised when category type does not match the transaction type."""


class CategoryNotAllowedForTransfer(TransactionError):
    """Raised when a transfer includes a category."""


class InvalidTransactionEntries(TransactionError):
    """Raised when entries violate type-specific posting rules."""


class SameAccountTransfer(TransactionError):
    """Raised when source and destination accounts are identical."""


class CrossCurrencyTransferNotSupported(TransactionError):
    """Raised when transferring between accounts with different currencies."""


class EntryCurrencyMismatch(TransactionError):
    """Raised when entry currency differs from the account currency."""
