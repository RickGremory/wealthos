"""Domain errors for the organizations module."""


class OrganizationError(Exception):
    """Base domain error for organizations."""


class OrganizationNameEmpty(OrganizationError):
    """Raised when an organization name is blank."""


class OrganizationNameTooLong(OrganizationError):
    """Raised when an organization name exceeds the allowed length."""


class OrganizationSlugInvalid(OrganizationError):
    """Raised when a slug is empty or not kebab-case."""


class InvalidCurrency(OrganizationError):
    """Raised when a currency code is not supported."""


class InvalidTimezone(OrganizationError):
    """Raised when a timezone identifier is invalid."""


class InvalidLocale(OrganizationError):
    """Raised when a locale string is invalid."""


class OrganizationNotFoundError(OrganizationError):
    """Raised when the organization cannot be found."""
