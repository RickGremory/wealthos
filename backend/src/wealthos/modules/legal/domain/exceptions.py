"""Domain errors for the legal module."""


class LegalError(Exception):
    """Base domain error for legal/consent flows."""


class LegalDocumentNotFound(LegalError):
    """Raised when an active legal document cannot be found."""


class LegalDocumentVersionOutdated(LegalError):
    """Raised when client acceptance versions do not match active documents."""

    code = "LEGAL_DOCUMENT_VERSION_OUTDATED"


class LegalAcceptanceRequired(LegalError):
    """Raised when required terms/privacy acceptances are missing."""

    code = "LEGAL_ACCEPTANCE_REQUIRED"


class InvalidLegalAcceptance(LegalError):
    """Raised when acceptance payload is malformed."""
