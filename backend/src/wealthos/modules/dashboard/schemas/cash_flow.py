"""Cash-flow response schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from wealthos.modules.dashboard.application.views.cash_flow import CashFlowSeriesView


class CashFlowPointResponse(BaseModel):
    period_start: date
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal


class CashFlowSeriesResponse(BaseModel):
    currency: str
    items: list[CashFlowPointResponse]


class CashFlowResponse(BaseModel):
    """Period income/expense series by currency.

    Transfers and adjustments are excluded. Voided transactions are excluded.
    Empty buckets are filled with zeros for charting.
    """

    granularity: str
    series: list[CashFlowSeriesResponse]

    @classmethod
    def from_views(
        cls,
        series: list[CashFlowSeriesView],
        granularity: str,
    ) -> CashFlowResponse:
        return cls(
            granularity=granularity,
            series=[
                CashFlowSeriesResponse(
                    currency=item.currency,
                    items=[
                        CashFlowPointResponse(
                            period_start=point.period_start,
                            income=point.income,
                            expenses=point.expenses,
                            net_cash_flow=point.net_cash_flow,
                        )
                        for point in item.items
                    ],
                )
                for item in series
            ],
        )
