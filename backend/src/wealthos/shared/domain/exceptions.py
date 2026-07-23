"""Shared domain exceptions."""


class SharedDomainError(Exception):
    """Base error for shared domain concepts."""


class InvalidCurrency(SharedDomainError):
    """Raised when a currency code is not supported."""


class CurrencyMismatch(SharedDomainError):
    """Raised when operating on Money values with different currencies."""
