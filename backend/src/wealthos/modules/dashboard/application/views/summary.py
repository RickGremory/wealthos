"""Dashboard summary read views."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CurrencyBalanceView:
    currency: str
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal


@dataclass(frozen=True, slots=True)
class CurrencyCashFlowView:
    currency: str
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal


@dataclass(frozen=True, slots=True)
class DashboardSummaryView:
    balances: tuple[CurrencyBalanceView, ...]
    cash_flow: tuple[CurrencyCashFlowView, ...]
    active_account_count: int
    archived_account_count: int
    transaction_count: int
