"""In-memory legal stubs for identity unit tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.legal.application.services.legal_consent_service import (
    ConsentContext,
    LegalAcceptanceItem,
)
from wealthos.modules.legal.domain.exceptions import (
    LegalAcceptanceRequired,
    LegalDocumentVersionOutdated,
)
from wealthos.modules.legal.domain.value_objects.document_types import (
    CONSENT_MARKETING,
    CONSENT_PRIVACY,
    CONSENT_TERMS,
    DOCUMENT_PRIVACY,
    DOCUMENT_TERMS,
    REQUIRED_REGISTRATION_TYPES,
)
from wealthos.modules.legal.infrastructure.models.legal_document_model import (
    LegalDocumentModel,
)


@dataclass
class _RecordedConsent:
    user_id: UUID
    organization_id: UUID | None
    document_type: str
    consent_type: str
    accepted: bool


@dataclass
class InMemoryLegalConsentService:
    """Minimal LegalConsentService stand-in for RegisterUserCommand unit tests."""

    active_versions: dict[str, str] = field(
        default_factory=lambda: {
            DOCUMENT_TERMS: "1.0",
            DOCUMENT_PRIVACY: "1.0",
        }
    )
    consents: list[_RecordedConsent] = field(default_factory=list)

    def validate_registration_acceptances(
        self,
        acceptances: list[LegalAcceptanceItem],
    ) -> dict[str, LegalDocumentModel]:
        by_type = {item.document_type: item for item in acceptances}
        resolved: dict[str, LegalDocumentModel] = {}
        now = datetime.now(UTC)
        for document_type in REQUIRED_REGISTRATION_TYPES:
            item = by_type.get(document_type)
            if item is None:
                raise LegalAcceptanceRequired(f"Missing acceptance for '{document_type}'.")
            expected = self.active_versions[document_type]
            if item.version != expected:
                raise LegalDocumentVersionOutdated(
                    f"Active version for '{document_type}' is '{expected}', got '{item.version}'."
                )
            if document_type == DOCUMENT_TERMS and item.accepted is not True:
                raise LegalAcceptanceRequired("Terms of service must be accepted.")
            if document_type == DOCUMENT_PRIVACY:
                ok = item.acknowledged if item.acknowledged is not None else item.accepted
                if ok is not True:
                    raise LegalAcceptanceRequired("Privacy notice must be acknowledged.")

            resolved[document_type] = LegalDocumentModel(
                id=uuid4(),
                document_type=document_type,
                version=expected,
                title=document_type,
                content_url=f"/legal/{document_type}",
                content_markdown="draft",
                content_hash="0" * 64,
                effective_at=now,
                published_at=now,
                is_active=True,
                requires_reacceptance=False,
                change_summary=None,
                created_at=now,
            )
        return resolved

    def record_registration_consents(
        self,
        *,
        user_id: UUID,
        organization_id: UUID | None,
        documents: dict[str, LegalDocumentModel],
        marketing_consent: bool,
        context: ConsentContext,
    ) -> None:
        self.consents.append(
            _RecordedConsent(
                user_id=user_id,
                organization_id=organization_id,
                document_type=DOCUMENT_TERMS,
                consent_type=CONSENT_TERMS,
                accepted=True,
            )
        )
        self.consents.append(
            _RecordedConsent(
                user_id=user_id,
                organization_id=organization_id,
                document_type=DOCUMENT_PRIVACY,
                consent_type=CONSENT_PRIVACY,
                accepted=True,
            )
        )
        if marketing_consent:
            self.consents.append(
                _RecordedConsent(
                    user_id=user_id,
                    organization_id=organization_id,
                    document_type=DOCUMENT_PRIVACY,
                    consent_type=CONSENT_MARKETING,
                    accepted=True,
                )
            )
