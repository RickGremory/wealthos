"""GetTaxReserveRecommendation query."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.application.queries.get_tax_summary import (
    GetTaxSummaryQuery,
    TaxSummary,
)

_ZERO = Decimal("0.00")


@dataclass(frozen=True, slots=True)
class TaxReserveRecommendation:
    currency: str
    estimated_tax: Decimal
    paid: Decimal
    reserve_balance: Decimal
    recommended_transfer: Decimal


class GetTaxReserveRecommendationQuery:
    def __init__(self, summary_query: GetTaxSummaryQuery) -> None:
        self._summary = summary_query

    def execute(self, organization_id: UUID) -> list[TaxReserveRecommendation]:
        summary: TaxSummary = self._summary.execute(organization_id)
        recommendations: list[TaxReserveRecommendation] = []
        for item in summary.by_currency:
            recommended = max(item.balance - item.reserve_balance, _ZERO)
            recommendations.append(
                TaxReserveRecommendation(
                    currency=item.currency,
                    estimated_tax=item.estimated_tax,
                    paid=item.paid,
                    reserve_balance=item.reserve_balance,
                    recommended_transfer=recommended,
                )
            )
        return recommendations
