"""Tax period detail read view."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from wealthos.modules.taxes.domain.entities.tax_calculation import TaxCalculation
from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod


@dataclass(frozen=True, slots=True)
class TaxPeriodDetail:
    period: TaxPeriod
    latest_calculation: TaxCalculation | None
    paid_amount: Decimal
    balance: Decimal
