"""SQLAlchemy MexicoTaxTransactionOverrideRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxTransactionOverride,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_transaction_override_mapper import (
    MexicoTaxTransactionOverrideMapper,
)
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import (
    MexicoTaxTransactionOverrideModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyMexicoTaxTransactionOverrideRepository(
    BaseRepository[MexicoTaxTransactionOverrideModel]
):
    def __init__(
        self, session: Session, mapper: MexicoTaxTransactionOverrideMapper | None = None
    ) -> None:
        super().__init__(session, MexicoTaxTransactionOverrideModel)
        self._mapper = mapper or MexicoTaxTransactionOverrideMapper()

    def add(self, override: MexicoTaxTransactionOverride) -> MexicoTaxTransactionOverride:
        model = self._mapper.to_model(override)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_transaction(
        self, organization_id: UUID, tax_profile_id: UUID, transaction_id: UUID
    ) -> MexicoTaxTransactionOverride | None:
        stmt = select(MexicoTaxTransactionOverrideModel).where(
            MexicoTaxTransactionOverrideModel.organization_id == organization_id,
            MexicoTaxTransactionOverrideModel.tax_profile_id == tax_profile_id,
            MexicoTaxTransactionOverrideModel.transaction_id == transaction_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_profile(
        self, organization_id: UUID, tax_profile_id: UUID
    ) -> list[MexicoTaxTransactionOverride]:
        stmt = select(MexicoTaxTransactionOverrideModel).where(
            MexicoTaxTransactionOverrideModel.organization_id == organization_id,
            MexicoTaxTransactionOverrideModel.tax_profile_id == tax_profile_id,
        )
        return [self._mapper.to_entity(m) for m in self.session.scalars(stmt)]

    def save(self, override: MexicoTaxTransactionOverride) -> MexicoTaxTransactionOverride:
        model = self.session.get(MexicoTaxTransactionOverrideModel, override.id)
        if model is None or model.organization_id != override.organization_id:
            raise LookupError("Override not found.")
        self._mapper.apply_to_model(override, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
