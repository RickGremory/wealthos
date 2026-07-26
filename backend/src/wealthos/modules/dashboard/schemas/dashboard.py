"""Aggregate dashboard projection response schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class DashboardOrganizationInfo(BaseModel):
    id: UUID
    name: str
    timezone: str
    currency: str


class DashboardPeriodInfo(BaseModel):
    date_from: date
    date_to: date
    timezone: str


class DashboardCurrencyMetrics(BaseModel):
    currency: str
    net_worth: Decimal
    liquid_balance: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_net_flow: Decimal


class WidgetAction(BaseModel):
    label: str
    to: str


class MetricsWidget(BaseModel):
    status: Literal["ready"] = "ready"


class OnboardingStepData(BaseModel):
    id: str
    label: str
    description: str
    completed: bool
    to: str


class OnboardingWidgetData(BaseModel):
    is_visible: bool
    completed: bool
    completed_steps: int
    total_steps: int
    steps: list[OnboardingStepData]


class OnboardingWidget(BaseModel):
    status: Literal["ready", "empty"]
    data: OnboardingWidgetData


class AttentionItemData(BaseModel):
    id: str
    severity: Literal["info", "warning", "critical"]
    title: str
    message: str
    amount: Decimal | None = None
    currency: str | None = None
    action_label: str
    action_to: str


class AttentionWidgetData(BaseModel):
    items: list[AttentionItemData]


class AttentionWidget(BaseModel):
    status: Literal["ready", "empty"]
    data: AttentionWidgetData


class ActivityNamedRef(BaseModel):
    id: UUID
    name: str


class ActivityItemData(BaseModel):
    id: UUID
    transaction_type: str
    description: str
    category: ActivityNamedRef | None
    occurred_at: datetime
    status: str
    amount: Decimal
    currency: str
    account: ActivityNamedRef | None = None


class ActivityWidgetData(BaseModel):
    items: list[ActivityItemData]


class ActivityWidget(BaseModel):
    status: Literal["ready", "empty", "error"]
    data: ActivityWidgetData | None = None
    error_code: str | None = None


class CashFlowPointData(BaseModel):
    period_start: date
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal


class CashFlowWidgetData(BaseModel):
    currency: str
    granularity: str
    income: Decimal
    expenses: Decimal
    net_cash_flow: Decimal
    points: list[CashFlowPointData]


class CashFlowWidget(BaseModel):
    status: Literal["ready", "empty", "error"]
    data: CashFlowWidgetData | None = None
    error_code: str | None = None


class UpcomingWidgetData(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)


class UpcomingWidget(BaseModel):
    status: Literal["not_configured", "empty", "ready"]
    data: UpcomingWidgetData


class SafeToSpendWidgetData(BaseModel):
    currency: str | None
    safe_to_spend: Decimal | None
    funding_gap: Decimal | None = None


class SafeToSpendWidget(BaseModel):
    status: Literal["available", "not_configured", "unavailable", "error"]
    data: SafeToSpendWidgetData | None = None
    action: WidgetAction | None = None
    error_code: str | None = None


class ModuleLineData(BaseModel):
    label: str
    value: str


class ModuleWidgetData(BaseModel):
    title: str
    lines: list[ModuleLineData] = Field(default_factory=list)
    hint: str | None = None


class ModuleWidget(BaseModel):
    status: Literal["available", "not_configured", "empty", "error"]
    data: ModuleWidgetData | None = None
    action: WidgetAction | None = None
    error_code: str | None = None


class DashboardWidgets(BaseModel):
    metrics: MetricsWidget
    onboarding: OnboardingWidget
    attention: AttentionWidget
    activity: ActivityWidget
    cash_flow: CashFlowWidget
    upcoming: UpcomingWidget
    safe_to_spend: SafeToSpendWidget
    budget: ModuleWidget
    goal: ModuleWidget
    debts: ModuleWidget
    taxes: ModuleWidget


class FinancialCommitmentsTotalByCurrency(BaseModel):
    currency: str
    total_obligations: Decimal
    monthly_payments: Decimal


class FinancialCommitmentsNextDue(BaseModel):
    commitment_id: UUID
    name: str
    due_in_days: int
    currency: str | None = None
    amount: Decimal | None = None


class FinancialCommitmentsAttentionItem(BaseModel):
    commitment_id: UUID
    code: str
    message: str
    currency: str | None = None


class FinancialCommitmentsProjection(BaseModel):
    status: Literal["ready", "empty", "error"] = "ready"
    active_count: int = 0
    overdue_count: int = 0
    totals_by_currency: list[FinancialCommitmentsTotalByCurrency] = Field(
        default_factory=list
    )
    next_due: FinancialCommitmentsNextDue | None = None
    attention: list[FinancialCommitmentsAttentionItem] = Field(default_factory=list)
    error_code: str | None = None


class DashboardResponse(BaseModel):
    """Single dashboard projection for the organization overview."""

    as_of: datetime
    organization: DashboardOrganizationInfo
    period: DashboardPeriodInfo
    currencies: list[DashboardCurrencyMetrics]
    selected_currency: str
    available_currencies: list[str]
    widgets: DashboardWidgets
    financial_commitments: FinancialCommitmentsProjection | None = None
