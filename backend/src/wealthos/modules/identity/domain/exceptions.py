"""Domain errors for the identity module."""


class IdentityError(Exception):
    """Base domain error for identity."""


class InvalidEmail(IdentityError):
    """Raised when an email address is invalid."""


class DisplayNameEmpty(IdentityError):
    """Raised when display_name is blank or too short."""


class DisplayNameTooLong(IdentityError):
    """Raised when display_name exceeds the allowed length."""


class UserNotFoundError(IdentityError):
    """Raised when the user cannot be found."""


class UserEmailAlreadyExists(IdentityError):
    """Raised when the email is already registered."""
