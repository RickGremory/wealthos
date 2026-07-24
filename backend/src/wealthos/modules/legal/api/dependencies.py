"""FastAPI dependencies for the legal module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.legal.application.services.legal_consent_service import (
    LegalConsentService,
)
from wealthos.modules.legal.infrastructure.repositories import (
    SqlAlchemyLegalConsentRepository,
    SqlAlchemyLegalDocumentRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_legal_consent_service(
    session: Annotated[Session, Depends(get_db)],
) -> LegalConsentService:
    return LegalConsentService(
        documents=SqlAlchemyLegalDocumentRepository(session),
        consents=SqlAlchemyLegalConsentRepository(session),
    )
