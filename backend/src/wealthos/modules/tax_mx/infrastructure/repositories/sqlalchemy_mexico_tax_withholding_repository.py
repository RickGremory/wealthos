"""SQLAlchemy MexicoTaxWithholdingRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.tax_mx.domain.entities.mexico_tax_withholding import MexicoTaxWithholding
from wealthos.modules.tax_mx.domain.value_objects.estimation import MexicoWithholdingType
from wealthos.modules.tax_mx.domain.value_objects.rfc import RFC
from wealthos.modules.tax_mx.infrastructure.models.tax_mx_models import MexicoTaxWithholdingModel
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.shared.base import BaseRepository
from wealthos.shared.domain.value_objects.money import Money


class SqlAlchemyMexicoTaxWithholdingRepository(BaseRepository[MexicoTaxWithholdingModel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, MexicoTaxWithholdingModel)

    def add(self, withholding: MexicoTaxWithholding) -> MexicoTaxWithholding:
        model = MexicoTaxWithholdingModel(
            id=withholding.id,
            organization_id=withholding.organization_id,
            transaction_id=withholding.transaction_id,
            withholding_type=withholding.withholding_type.value,
            base_amount=withholding.base_amount.amount,
            rate=withholding.rate.value if withholding.rate else None,
            amount=withholding.amount.amount,
            currency=withholding.amount.currency.value,
            withheld_by_rfc=(
                withholding.withheld_by_rfc.value if withholding.withheld_by_rfc else None
            ),
            created_at=withholding.created_at,
            updated_at=withholding.updated_at,
        )
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._to_entity(model)

    def list_by_transactions(
        self, organization_id: UUID, transaction_ids: list[UUID]
    ) -> list[MexicoTaxWithholding]:
        if not transaction_ids:
            return []
        stmt = select(MexicoTaxWithholdingModel).where(
            MexicoTaxWithholdingModel.organization_id == organization_id,
            MexicoTaxWithholdingModel.transaction_id.in_(transaction_ids),
        )
        return [self._to_entity(m) for m in self.session.scalars(stmt)]

    def _to_entity(self, model: MexicoTaxWithholdingModel) -> MexicoTaxWithholding:
        return MexicoTaxWithholding(
            id=model.id,
            organization_id=model.organization_id,
            transaction_id=model.transaction_id,
            withholding_type=MexicoWithholdingType(model.withholding_type),
            base_amount=Money(model.base_amount, model.currency),
            rate=Percentage(model.rate) if model.rate is not None else None,
            amount=Money(model.amount, model.currency),
            withheld_by_rfc=RFC(model.withheld_by_rfc) if model.withheld_by_rfc else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
