"""SQLAlchemy TaxTransactionOverrideRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_transaction_override import (
    TaxTransactionOverride,
)
from wealthos.modules.taxes.infrastructure.mappers.tax_transaction_override_mapper import (
    TaxTransactionOverrideMapper,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import (
    TaxTransactionOverrideModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxTransactionOverrideRepository(BaseRepository[TaxTransactionOverrideModel]):
    def __init__(
        self,
        session: Session,
        mapper: TaxTransactionOverrideMapper | None = None,
    ) -> None:
        super().__init__(session, TaxTransactionOverrideModel)
        self._mapper = mapper or TaxTransactionOverrideMapper()

    def upsert(self, override: TaxTransactionOverride) -> TaxTransactionOverride:
        existing = self.get_by_transaction(
            override.organization_id,
            override.tax_profile_id,
            override.transaction_id,
        )
        if existing is None:
            model = self._mapper.to_model(override)
            super().add(model)
            self.flush()
            self.refresh(model)
            return self._mapper.to_entity(model)

        model = self.session.get(TaxTransactionOverrideModel, existing.id)
        assert model is not None
        existing.update(
            tax_treatment=override.tax_treatment.value,
            deductibility_percentage=override.deductibility_percentage.value,
            reason=override.reason,
        )
        self._mapper.apply_to_model(existing, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
    ) -> list[TaxTransactionOverride]:
        stmt = select(TaxTransactionOverrideModel).where(
            TaxTransactionOverrideModel.organization_id == organization_id,
            TaxTransactionOverrideModel.tax_profile_id == tax_profile_id,
        )
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def get_by_transaction(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        transaction_id: UUID,
    ) -> TaxTransactionOverride | None:
        stmt = select(TaxTransactionOverrideModel).where(
            TaxTransactionOverrideModel.organization_id == organization_id,
            TaxTransactionOverrideModel.tax_profile_id == tax_profile_id,
            TaxTransactionOverrideModel.transaction_id == transaction_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None
