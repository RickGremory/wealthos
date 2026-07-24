"""Repository ports for legal documents and consents."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.legal.infrastructure.models.legal_consent_model import (
    LegalConsentModel,
)
from wealthos.modules.legal.infrastructure.models.legal_document_model import (
    LegalDocumentModel,
)


class LegalDocumentRepository(Protocol):
    def get_active_by_type(self, document_type: str) -> LegalDocumentModel | None: ...

    def get_by_type_and_version(
        self,
        document_type: str,
        version: str,
    ) -> LegalDocumentModel | None: ...

    def list_active(self) -> list[LegalDocumentModel]: ...


class LegalConsentRepository(Protocol):
    def add(self, consent: LegalConsentModel) -> LegalConsentModel: ...

    def list_for_user(self, user_id: UUID) -> list[LegalConsentModel]: ...

    def has_accepted(
        self,
        user_id: UUID,
        legal_document_id: UUID,
        consent_type: str,
    ) -> bool: ...

    def latest_marketing_consent(self, user_id: UUID) -> LegalConsentModel | None: ...

    def list_accepted_document_consents(
        self,
        user_id: UUID,
    ) -> list[tuple[LegalConsentModel, LegalDocumentModel]]: ...
