"""SQLAlchemy TaxEvidenceRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.domain.entities.tax_evidence import TaxEvidence
from wealthos.modules.tax_mx.infrastructure.mappers.tax_evidence_mapper import TaxEvidenceMapper
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import TaxEvidenceModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxEvidenceRepository(BaseRepository[TaxEvidenceModel]):
    def __init__(self, session: Session, mapper: TaxEvidenceMapper | None = None) -> None:
        super().__init__(session, TaxEvidenceModel)
        self._mapper = mapper or TaxEvidenceMapper()

    def add(self, evidence: TaxEvidence) -> TaxEvidence:
        model = self._mapper.to_model(evidence)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_by_transaction(self, organization_id: UUID, transaction_id: UUID) -> list[TaxEvidence]:
        stmt = select(TaxEvidenceModel).where(
            TaxEvidenceModel.organization_id == organization_id,
            TaxEvidenceModel.transaction_id == transaction_id,
        )
        return [self._mapper.to_entity(m) for m in self.session.scalars(stmt)]

    def latest_status_by_transactions(
        self, organization_id: UUID, transaction_ids: list[UUID]
    ) -> dict[UUID, str]:
        if not transaction_ids:
            return {}
        stmt = (
            select(TaxEvidenceModel)
            .where(
                TaxEvidenceModel.organization_id == organization_id,
                TaxEvidenceModel.transaction_id.in_(transaction_ids),
            )
            .order_by(TaxEvidenceModel.updated_at.desc())
        )
        result: dict[UUID, str] = {}
        for model in self.session.scalars(stmt):
            if model.transaction_id not in result:
                result[model.transaction_id] = model.validation_status
        return result

    def save(self, evidence: TaxEvidence) -> TaxEvidence:
        model = self.session.get(TaxEvidenceModel, evidence.id)
        if model is None:
            raise LookupError("Evidence not found.")
        self._mapper.apply_to_model(evidence, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
