"""Domain errors for the accounts module."""


class AccountError(Exception):
    """Base domain error for accounts."""


class AccountNameEmpty(AccountError):
    """Raised when an account name is blank or too short."""


class AccountNameTooLong(AccountError):
    """Raised when an account name exceeds the allowed length."""


class InvalidAccountType(AccountError):
    """Raised when an account type is not supported."""


class InvalidLastFour(AccountError):
    """Raised when last_four is not a 4-digit string."""


class AccountNotFoundError(AccountError):
    """Raised when the account cannot be found in the organization."""


class AccountAlreadyArchived(AccountError):
    """Raised when archiving an already archived account."""
