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


class WeakPassword(IdentityError):
    """Raised when a password does not meet policy."""


class InvalidCredentials(IdentityError):
    """Raised when email/password authentication fails."""


class InactiveUser(IdentityError):
    """Raised when an inactive user attempts to authenticate."""


class InvalidAccessToken(IdentityError):
    """Raised when an access token is missing, expired, or invalid."""
