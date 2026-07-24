"""SQLAlchemy models for legal documents and consents."""

from wealthos.modules.legal.infrastructure.models.legal_consent_model import (
    LegalConsentModel,
)
from wealthos.modules.legal.infrastructure.models.legal_document_model import (
    LegalDocumentModel,
)

__all__ = ["LegalConsentModel", "LegalDocumentModel"]
