"""Application service for legal documents and consents."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from wealthos.modules.legal.domain.exceptions import (
    InvalidLegalAcceptance,
    LegalAcceptanceRequired,
    LegalDocumentNotFound,
    LegalDocumentVersionOutdated,
)
from wealthos.modules.legal.domain.repositories.legal_repository import (
    LegalConsentRepository,
    LegalDocumentRepository,
)
from wealthos.modules.legal.domain.value_objects.document_types import (
    CONSENT_MARKETING,
    CONSENT_PRIVACY,
    CONSENT_TERMS,
    CONSENT_TYPE_BY_DOCUMENT,
    DOCUMENT_COOKIES,
    DOCUMENT_PRIVACY,
    DOCUMENT_TERMS,
    REQUIRED_REGISTRATION_TYPES,
    SOURCE_FORCED_REACCEPTANCE,
    SOURCE_REGISTRATION,
    SOURCE_SETTINGS,
)
from wealthos.modules.legal.infrastructure.models.legal_consent_model import (
    LegalConsentModel,
)
from wealthos.modules.legal.infrastructure.models.legal_document_model import (
    LegalDocumentModel,
)


@dataclass(frozen=True, slots=True)
class LegalAcceptanceItem:
    document_type: str
    version: str
    accepted: bool | None = None
    acknowledged: bool | None = None


@dataclass(frozen=True, slots=True)
class PendingDocument:
    document_type: str
    version: str
    title: str
    url: str


@dataclass(frozen=True, slots=True)
class ComplianceStatus:
    is_compliant: bool
    pending_documents: list[PendingDocument]


@dataclass(frozen=True, slots=True)
class ConsentContext:
    ip_address: str | None = None
    user_agent: str | None = None
    organization_id: UUID | None = None
    source: str = SOURCE_REGISTRATION


class LegalConsentService:
    """Validate and record legal consents; evaluate compliance."""

    def __init__(
        self,
        *,
        documents: LegalDocumentRepository,
        consents: LegalConsentRepository,
    ) -> None:
        self._documents = documents
        self._consents = consents

    def get_active_document(self, document_type: str) -> LegalDocumentModel:
        doc = self._documents.get_active_by_type(document_type)
        if doc is None:
            raise LegalDocumentNotFound(f"No active document for type '{document_type}'.")
        return doc

    def list_active_documents(self) -> list[LegalDocumentModel]:
        return self._documents.list_active()

    def registration_requirements(self) -> dict:
        terms = self.get_active_document(DOCUMENT_TERMS)
        privacy = self.get_active_document(DOCUMENT_PRIVACY)
        return {
            "documents": [
                {
                    "type": terms.document_type,
                    "version": terms.version,
                    "title": terms.title,
                    "url": terms.content_url,
                    "acceptance_required": True,
                },
                {
                    "type": privacy.document_type,
                    "version": privacy.version,
                    "title": privacy.title,
                    "url": privacy.content_url,
                    "acknowledgement_required": True,
                },
            ],
            "marketing_consent": {"available": True, "required": False},
        }

    def validate_registration_acceptances(
        self,
        acceptances: list[LegalAcceptanceItem],
    ) -> dict[str, LegalDocumentModel]:
        by_type = {item.document_type: item for item in acceptances}
        resolved: dict[str, LegalDocumentModel] = {}

        for document_type in REQUIRED_REGISTRATION_TYPES:
            active = self.get_active_document(document_type)
            item = by_type.get(document_type)
            if item is None:
                raise LegalAcceptanceRequired(
                    f"Missing acceptance for '{document_type}'."
                )
            if item.version != active.version:
                raise LegalDocumentVersionOutdated(
                    f"Active version for '{document_type}' is '{active.version}', "
                    f"got '{item.version}'."
                )

            if document_type == DOCUMENT_TERMS:
                if item.accepted is not True:
                    raise LegalAcceptanceRequired(
                        "Terms of service must be accepted."
                    )
            elif document_type == DOCUMENT_PRIVACY:
                acknowledged = item.acknowledged if item.acknowledged is not None else item.accepted
                if acknowledged is not True:
                    raise LegalAcceptanceRequired(
                        "Privacy notice must be acknowledged."
                    )

            resolved[document_type] = active

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
        now = datetime.now(UTC)
        ctx = ConsentContext(
            ip_address=context.ip_address,
            user_agent=_trim_ua(context.user_agent),
            organization_id=organization_id,
            source=SOURCE_REGISTRATION,
        )

        self._consents.add(
            self._build_consent(
                user_id=user_id,
                document=documents[DOCUMENT_TERMS],
                consent_type=CONSENT_TERMS,
                accepted=True,
                accepted_at=now,
                context=ctx,
            )
        )
        self._consents.add(
            self._build_consent(
                user_id=user_id,
                document=documents[DOCUMENT_PRIVACY],
                consent_type=CONSENT_PRIVACY,
                accepted=True,
                accepted_at=now,
                context=ctx,
            )
        )
        if marketing_consent:
            self._consents.add(
                self._build_consent(
                    user_id=user_id,
                    document=documents[DOCUMENT_PRIVACY],
                    consent_type=CONSENT_MARKETING,
                    accepted=True,
                    accepted_at=now,
                    context=ctx,
                )
            )

    def get_compliance_status(self, user_id: UUID) -> ComplianceStatus:
        pending: list[PendingDocument] = []
        for doc in self._documents.list_active():
            if not self._document_requires_compliance(doc):
                continue
            consent_type = CONSENT_TYPE_BY_DOCUMENT.get(doc.document_type)
            if consent_type is None:
                # Cookie policy (or unknown) only when requires_reacceptance.
                continue
            if not self._consents.has_accepted(user_id, doc.id, consent_type):
                pending.append(
                    PendingDocument(
                        document_type=doc.document_type,
                        version=doc.version,
                        title=doc.title,
                        url=doc.content_url,
                    )
                )
        return ComplianceStatus(is_compliant=len(pending) == 0, pending_documents=pending)

    def record_acceptances(
        self,
        *,
        user_id: UUID,
        acceptances: list[LegalAcceptanceItem],
        context: ConsentContext,
    ) -> ComplianceStatus:
        now = datetime.now(UTC)
        ctx = ConsentContext(
            ip_address=context.ip_address,
            user_agent=_trim_ua(context.user_agent),
            organization_id=context.organization_id,
            source=context.source or SOURCE_FORCED_REACCEPTANCE,
        )

        for item in acceptances:
            if item.document_type not in CONSENT_TYPE_BY_DOCUMENT:
                raise InvalidLegalAcceptance(
                    f"Unsupported document type '{item.document_type}'."
                )
            active = self.get_active_document(item.document_type)
            if item.version != active.version:
                raise LegalDocumentVersionOutdated(
                    f"Active version for '{item.document_type}' is '{active.version}', "
                    f"got '{item.version}'."
                )

            ok = (
                item.accepted is True
                or item.acknowledged is True
            )
            if not ok:
                raise LegalAcceptanceRequired(
                    f"Document '{item.document_type}' must be accepted."
                )

            self._consents.add(
                self._build_consent(
                    user_id=user_id,
                    document=active,
                    consent_type=CONSENT_TYPE_BY_DOCUMENT[item.document_type],
                    accepted=True,
                    accepted_at=now,
                    context=ctx,
                )
            )

        return self.get_compliance_status(user_id)

    def list_user_documents(self, user_id: UUID) -> dict:
        rows = self._consents.list_accepted_document_consents(user_id)
        # Deduplicate by document_type keeping latest acceptance.
        seen: set[str] = set()
        items: list[dict] = []
        for consent, document in rows:
            if document.document_type in seen:
                continue
            seen.add(document.document_type)
            items.append(
                {
                    "type": document.document_type,
                    "version": document.version,
                    "title": document.title,
                    "url": document.content_url,
                    "accepted_at": consent.accepted_at,
                    "consent_type": consent.consent_type,
                }
            )

        marketing = self._consents.latest_marketing_consent(user_id)
        marketing_opted_in = bool(
            marketing
            and marketing.accepted
            and marketing.withdrawn_at is None
        )

        return {
            "documents": items,
            "marketing_consent": {
                "opted_in": marketing_opted_in,
                "updated_at": marketing.accepted_at if marketing else None,
            },
        }

    def set_marketing_consent(
        self,
        *,
        user_id: UUID,
        accepted: bool,
        context: ConsentContext,
    ) -> dict:
        privacy = self.get_active_document(DOCUMENT_PRIVACY)
        now = datetime.now(UTC)
        ctx = ConsentContext(
            ip_address=context.ip_address,
            user_agent=_trim_ua(context.user_agent),
            organization_id=context.organization_id,
            source=SOURCE_SETTINGS,
        )
        consent = self._build_consent(
            user_id=user_id,
            document=privacy,
            consent_type=CONSENT_MARKETING,
            accepted=accepted,
            accepted_at=now,
            context=ctx,
        )
        if not accepted:
            consent.withdrawn_at = now
        self._consents.add(consent)
        return {
            "opted_in": accepted,
            "updated_at": now,
        }

    def _document_requires_compliance(self, doc: LegalDocumentModel) -> bool:
        if doc.document_type in REQUIRED_REGISTRATION_TYPES:
            return True
        if doc.document_type == DOCUMENT_COOKIES:
            return bool(doc.requires_reacceptance)
        return bool(doc.requires_reacceptance)

    def _build_consent(
        self,
        *,
        user_id: UUID,
        document: LegalDocumentModel,
        consent_type: str,
        accepted: bool,
        accepted_at: datetime,
        context: ConsentContext,
    ) -> LegalConsentModel:
        return LegalConsentModel(
            id=uuid4(),
            user_id=user_id,
            organization_id=context.organization_id,
            legal_document_id=document.id,
            consent_type=consent_type,
            accepted=accepted,
            accepted_at=accepted_at,
            withdrawn_at=None,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            source=context.source,
            created_at=accepted_at,
        )


def _trim_ua(user_agent: str | None) -> str | None:
    if user_agent is None:
        return None
    return user_agent[:512]
