"""TaxPeriod aggregate — calculable fiscal window."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.exceptions import (
    InvalidTaxPeriod,
    TaxPeriodAlreadyClosed,
    TaxPeriodClosed,
    TaxPeriodNotCalculated,
)
from wealthos.modules.taxes.domain.value_objects.tax_period_status import TaxPeriodStatus
from wealthos.modules.taxes.domain.value_objects.tax_period_type import TaxPeriodType
from wealthos.shared.domain.value_objects.currency import Currency


@dataclass(slots=True)
class TaxPeriod:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    period_type: TaxPeriodType
    date_from: date
    date_to: date
    status: TaxPeriodStatus
    currency: Currency
    calculated_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        period_type: str,
        date_from: date,
        date_to: date,
        currency: str,
        period_id: UUID | None = None,
    ) -> TaxPeriod:
        if date_to < date_from:
            raise InvalidTaxPeriod("date_to cannot be before date_from.")
        now = datetime.now(UTC)
        return cls(
            id=period_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            period_type=TaxPeriodType(period_type),
            date_from=date_from,
            date_to=date_to,
            status=TaxPeriodStatus("open"),
            currency=Currency(currency),
            calculated_at=None,
            closed_at=None,
            created_at=now,
            updated_at=now,
        )

    def mark_calculated(self) -> None:
        if self.status.value == "closed":
            raise TaxPeriodClosed("Cannot recalculate a closed tax period.")
        now = datetime.now(UTC)
        self.status = TaxPeriodStatus("calculated")
        self.calculated_at = now
        self.updated_at = now

    def close(self) -> None:
        if self.status.value == "closed":
            raise TaxPeriodAlreadyClosed("Tax period is already closed.")
        if self.status.value != "calculated":
            raise TaxPeriodNotCalculated("Tax period must be calculated before closing.")
        now = datetime.now(UTC)
        self.status = TaxPeriodStatus("closed")
        self.closed_at = now
        self.updated_at = now

    def ensure_can_calculate(self) -> None:
        if self.status.value == "closed":
            raise TaxPeriodClosed("Cannot recalculate a closed tax period.")
