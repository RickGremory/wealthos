"""SQLAlchemy MexicoTaxDetailsRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_details_mapper import (
    MexicoTaxDetailsMapper,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTransactionTaxDetailsModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyMexicoTaxDetailsRepository(BaseRepository[MexicoTransactionTaxDetailsModel]):
    def __init__(self, session: Session, mapper: MexicoTaxDetailsMapper | None = None) -> None:
        super().__init__(session, MexicoTransactionTaxDetailsModel)
        self._mapper = mapper or MexicoTaxDetailsMapper()

    def add(self, details: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetails:
        model = self._mapper.to_model(details)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_transaction(
        self, organization_id: UUID, transaction_id: UUID
    ) -> MexicoTransactionTaxDetails | None:
        stmt = select(MexicoTransactionTaxDetailsModel).where(
            MexicoTransactionTaxDetailsModel.organization_id == organization_id,
            MexicoTransactionTaxDetailsModel.transaction_id == transaction_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_transactions(
        self, organization_id: UUID, transaction_ids: list[UUID]
    ) -> list[MexicoTransactionTaxDetails]:
        if not transaction_ids:
            return []
        stmt = select(MexicoTransactionTaxDetailsModel).where(
            MexicoTransactionTaxDetailsModel.organization_id == organization_id,
            MexicoTransactionTaxDetailsModel.transaction_id.in_(transaction_ids),
        )
        return [self._mapper.to_entity(m) for m in self.session.scalars(stmt)]

    def upsert(self, details: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetails:
        existing = self.get_by_transaction(details.organization_id, details.transaction_id)
        if existing is None:
            return self.add(details)

        replacement = MexicoTransactionTaxDetails.create(
            organization_id=details.organization_id,
            transaction_id=details.transaction_id,
            subtotal=details.subtotal,
            vat_amount=details.vat_amount,
            total=details.total,
            withheld_income_tax=details.withheld_income_tax,
            withheld_vat=details.withheld_vat,
            other_taxes=details.other_taxes,
            calculation_source=details.calculation_source,
            details_id=existing.id,
        )
        replacement.created_at = existing.created_at
        return self.save(replacement)

    def save(self, details: MexicoTransactionTaxDetails) -> MexicoTransactionTaxDetails:
        model = self.session.get(MexicoTransactionTaxDetailsModel, details.id)
        if model is None:
            raise LookupError("Details not found.")
        refreshed = self._mapper.to_model(details)
        for col in (
            "subtotal",
            "vat_amount",
            "withheld_income_tax",
            "withheld_vat",
            "other_taxes",
            "total",
            "currency",
            "calculation_source",
            "updated_at",
        ):
            setattr(model, col, getattr(refreshed, col))
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
