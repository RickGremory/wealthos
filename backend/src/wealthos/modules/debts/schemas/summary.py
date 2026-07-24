"""Debt summary response schema."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.debts.application.queries.get_debt_summary import DebtSummary


class DebtSummaryByCurrencyResponse(BaseModel):
    currency: str
    total_debt: Decimal
    total_minimum_payments: Decimal
    weighted_average_rate: Decimal
    active_debt_count: int
    highest_interest_debt_id: UUID | None
    highest_interest_rate: Decimal | None


class DebtSummaryResponse(BaseModel):
    by_currency: list[DebtSummaryByCurrencyResponse]

    @classmethod
    def from_summary(cls, summary: DebtSummary) -> DebtSummaryResponse:
        return cls(
            by_currency=[
                DebtSummaryByCurrencyResponse(
                    currency=item.currency,
                    total_debt=item.total_debt,
                    total_minimum_payments=item.total_minimum_payments,
                    weighted_average_rate=item.weighted_average_rate,
                    active_debt_count=item.active_debt_count,
                    highest_interest_debt_id=item.highest_interest_debt_id,
                    highest_interest_rate=item.highest_interest_rate,
                )
                for item in summary.by_currency
            ]
        )
