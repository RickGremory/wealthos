"""Dashboard summary response schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from wealthos.modules.dashboard.application.value_objects.date_range import DateRange
from wealthos.modules.dashboard.application.views.summary import DashboardSummaryView


class PeriodInfo(BaseModel):
    date_from: date
    date_to: date
    timezone: str


class CurrencyBalanceResponse(BaseModel):
    currency: str
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal


class CurrencyCashFlowResponse(BaseModel):
    currency: str
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal


class AccountCountResponse(BaseModel):
    active: int
    archived: int


class DashboardSummaryResponse(BaseModel):
    """Current balances + period cash flow.

    balances / net worth reflect the current account state (not historical).
    cash_flow reflects only posted income/expense in the selected period.
    Amounts are grouped by currency; no FX conversion is applied.
    Expenses and liabilities are positive display values.
    """

    period: PeriodInfo
    balances: list[CurrencyBalanceResponse]
    cash_flow: list[CurrencyCashFlowResponse]
    account_count: AccountCountResponse
    transaction_count: int = Field(
        description="Transactions with occurred_at in the selected period (any status).",
    )

    @classmethod
    def from_view(
        cls,
        view: DashboardSummaryView,
        date_range: DateRange,
    ) -> DashboardSummaryResponse:
        return cls(
            period=PeriodInfo(
                date_from=date_range.display_from,
                date_to=date_range.display_to,
                timezone=date_range.timezone,
            ),
            balances=[
                CurrencyBalanceResponse(
                    currency=item.currency,
                    total_assets=item.total_assets,
                    total_liabilities=item.total_liabilities,
                    net_worth=item.net_worth,
                )
                for item in view.balances
            ],
            cash_flow=[
                CurrencyCashFlowResponse(
                    currency=item.currency,
                    income=item.income,
                    expenses=item.expenses,
                    net_cash_flow=item.net_cash_flow,
                )
                for item in view.cash_flow
            ],
            account_count=AccountCountResponse(
                active=view.active_account_count,
                archived=view.archived_account_count,
            ),
            transaction_count=view.transaction_count,
        )
