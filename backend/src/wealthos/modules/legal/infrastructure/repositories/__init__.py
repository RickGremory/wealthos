"""SQLAlchemy repositories for legal documents and consents."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.legal.infrastructure.models.legal_consent_model import (
    LegalConsentModel,
)
from wealthos.modules.legal.infrastructure.models.legal_document_model import (
    LegalDocumentModel,
)


class SqlAlchemyLegalDocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active_by_type(self, document_type: str) -> LegalDocumentModel | None:
        stmt = select(LegalDocumentModel).where(
            LegalDocumentModel.document_type == document_type,
            LegalDocumentModel.is_active.is_(True),
        )
        return self._session.scalar(stmt)

    def get_by_type_and_version(
        self,
        document_type: str,
        version: str,
    ) -> LegalDocumentModel | None:
        stmt = select(LegalDocumentModel).where(
            LegalDocumentModel.document_type == document_type,
            LegalDocumentModel.version == version,
        )
        return self._session.scalar(stmt)

    def list_active(self) -> list[LegalDocumentModel]:
        stmt = (
            select(LegalDocumentModel)
            .where(LegalDocumentModel.is_active.is_(True))
            .order_by(LegalDocumentModel.document_type)
        )
        return list(self._session.scalars(stmt).all())


class SqlAlchemyLegalConsentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, consent: LegalConsentModel) -> LegalConsentModel:
        self._session.add(consent)
        self._session.flush()
        return consent

    def list_for_user(self, user_id: UUID) -> list[LegalConsentModel]:
        stmt = (
            select(LegalConsentModel)
            .where(LegalConsentModel.user_id == user_id)
            .order_by(LegalConsentModel.created_at.desc())
        )
        return list(self._session.scalars(stmt).all())

    def has_accepted(
        self,
        user_id: UUID,
        legal_document_id: UUID,
        consent_type: str,
    ) -> bool:
        stmt = (
            select(LegalConsentModel.id)
            .where(
                LegalConsentModel.user_id == user_id,
                LegalConsentModel.legal_document_id == legal_document_id,
                LegalConsentModel.consent_type == consent_type,
                LegalConsentModel.accepted.is_(True),
                LegalConsentModel.withdrawn_at.is_(None),
            )
            .limit(1)
        )
        return self._session.scalar(stmt) is not None

    def latest_marketing_consent(self, user_id: UUID) -> LegalConsentModel | None:
        from wealthos.modules.legal.domain.value_objects.document_types import (
            CONSENT_MARKETING,
        )

        stmt = (
            select(LegalConsentModel)
            .where(
                LegalConsentModel.user_id == user_id,
                LegalConsentModel.consent_type == CONSENT_MARKETING,
            )
            .order_by(LegalConsentModel.created_at.desc())
            .limit(1)
        )
        return self._session.scalar(stmt)

    def list_accepted_document_consents(
        self,
        user_id: UUID,
    ) -> list[tuple[LegalConsentModel, LegalDocumentModel]]:
        from wealthos.modules.legal.domain.value_objects.document_types import (
            CONSENT_MARKETING,
        )

        stmt = (
            select(LegalConsentModel, LegalDocumentModel)
            .join(
                LegalDocumentModel,
                LegalConsentModel.legal_document_id == LegalDocumentModel.id,
            )
            .where(
                LegalConsentModel.user_id == user_id,
                LegalConsentModel.accepted.is_(True),
                LegalConsentModel.consent_type != CONSENT_MARKETING,
            )
            .order_by(LegalConsentModel.accepted_at.desc())
        )
        return list(self._session.execute(stmt).all())
