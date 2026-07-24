"""GetTaxPeriod query."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.application.views.tax_period_detail import TaxPeriodDetail
from wealthos.modules.taxes.domain.exceptions import TaxPeriodNotFound
from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_payment_repository import (
    TaxPaymentRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)

_ZERO = Decimal("0.00")


class GetTaxPeriodQuery:
    def __init__(
        self,
        periods: TaxPeriodRepository,
        calculations: TaxCalculationRepository,
        payments: TaxPaymentRepository,
    ) -> None:
        self._periods = periods
        self._calculations = calculations
        self._payments = payments

    def execute(self, organization_id: UUID, period_id: UUID) -> TaxPeriodDetail:
        period = self._periods.get_by_id(organization_id, period_id)
        if period is None:
            raise TaxPeriodNotFound("Tax period not found.")

        latest = self._calculations.get_latest_by_period(organization_id, period_id)
        paid = self._payments.sum_by_period(
            organization_id,
            period_id,
            currency=period.currency.value,
        )
        estimated = latest.estimated_tax.amount if latest else _ZERO
        balance = max(estimated - paid, _ZERO)
        return TaxPeriodDetail(
            period=period,
            latest_calculation=latest,
            paid_amount=paid,
            balance=balance,
        )
