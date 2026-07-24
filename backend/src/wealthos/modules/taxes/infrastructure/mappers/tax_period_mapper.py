"""Map TaxPeriod ↔ TaxPeriodModel."""

from __future__ import annotations

from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.domain.value_objects.tax_period_status import TaxPeriodStatus
from wealthos.modules.taxes.domain.value_objects.tax_period_type import TaxPeriodType
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxPeriodModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.currency import Currency


class TaxPeriodMapper(BaseMapper[TaxPeriodModel, TaxPeriod]):
    def to_entity(self, model: TaxPeriodModel) -> TaxPeriod:
        return TaxPeriod(
            id=model.id,
            organization_id=model.organization_id,
            tax_profile_id=model.tax_profile_id,
            period_type=TaxPeriodType(model.period_type),
            date_from=model.date_from,
            date_to=model.date_to,
            status=TaxPeriodStatus(model.status),
            currency=Currency(model.currency),
            calculated_at=model.calculated_at,
            closed_at=model.closed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: TaxPeriod) -> TaxPeriodModel:
        return TaxPeriodModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            period_type=entity.period_type.value,
            date_from=entity.date_from,
            date_to=entity.date_to,
            status=entity.status.value,
            currency=entity.currency.value,
            calculated_at=entity.calculated_at,
            closed_at=entity.closed_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def apply_to_model(self, entity: TaxPeriod, model: TaxPeriodModel) -> TaxPeriodModel:
        model.status = entity.status.value
        model.calculated_at = entity.calculated_at
        model.closed_at = entity.closed_at
        model.updated_at = entity.updated_at
        return model
