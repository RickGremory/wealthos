"""Compare tax period calculation freshness against domain changes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wealthos.modules.tax_mx.domain.repositories.mexico_tax_read_repository import (
    MexicoTaxReadRepository,
)
from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod


@dataclass(frozen=True, slots=True)
class TaxPeriodStalenessResult:
    is_stale: bool
    calculated_at: datetime | None
    latest_relevant_change_at: datetime | None


class TaxPeriodStalenessService:
    def __init__(self, read: MexicoTaxReadRepository) -> None:
        self._read = read

    def evaluate(self, period: TaxPeriod, organization_id: UUID) -> TaxPeriodStalenessResult:
        latest = self._read.latest_relevant_change_at(
            organization_id,
            date_from=period.date_from,
            date_to=period.date_to,
        )
        calculated_at = period.calculated_at
        if calculated_at is None or latest is None:
            return TaxPeriodStalenessResult(
                is_stale=calculated_at is None and latest is not None,
                calculated_at=calculated_at,
                latest_relevant_change_at=latest,
            )
        return TaxPeriodStalenessResult(
            is_stale=latest > calculated_at,
            calculated_at=calculated_at,
            latest_relevant_change_at=latest,
        )
