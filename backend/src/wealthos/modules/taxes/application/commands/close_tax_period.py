"""CloseTaxPeriod command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod
from wealthos.modules.taxes.domain.exceptions import TaxPeriodNotFound
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)


@dataclass(frozen=True, slots=True)
class CloseTaxPeriodInput:
    organization_id: UUID
    period_id: UUID


class CloseTaxPeriodCommand:
    def __init__(self, periods: TaxPeriodRepository) -> None:
        self._periods = periods

    def execute(self, data: CloseTaxPeriodInput) -> TaxPeriod:
        period = self._periods.lock_for_update(data.organization_id, data.period_id)
        if period is None:
            raise TaxPeriodNotFound("Tax period not found.")
        period.close()
        return self._periods.save(period)
