"""Domain errors for the organizations module."""


class OrganizationsError(Exception):
    """Base domain error."""


class OrganizationsNotFoundError(OrganizationsError):
    """Raised when the aggregate cannot be found."""
