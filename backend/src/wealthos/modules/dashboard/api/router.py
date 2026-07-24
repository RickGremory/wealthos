"""HTTP routes for organization dashboard read models."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from wealthos.core.security.organization_context import OrganizationAccess
from wealthos.modules.dashboard.api.dependencies import (
    get_account_summary_query,
    get_cash_flow_query,
    get_debts_dashboard_query,
    get_goals_dashboard_query,
    get_recent_transactions_query,
    get_spending_query,
    get_summary_query,
)
from wealthos.modules.dashboard.application.queries.get_account_summary import (
    GetAccountSummaryQuery,
)
from wealthos.modules.dashboard.application.queries.get_cash_flow import GetCashFlowQuery
from wealthos.modules.dashboard.application.queries.get_dashboard_summary import (
    GetDashboardSummaryQuery,
)
from wealthos.modules.dashboard.application.queries.get_recent_transactions import (
    GetRecentTransactionsQuery,
)
from wealthos.modules.dashboard.application.queries.get_spending_by_category import (
    GetSpendingByCategoryQuery,
)
from wealthos.modules.dashboard.application.queries.period_filters import (
    DashboardPeriodFilters,
)
from wealthos.modules.dashboard.domain.value_objects.dashboard_period import (
    DashboardPeriod,
)
from wealthos.modules.dashboard.schemas.account_summary import AccountSummaryResponse
from wealthos.modules.dashboard.schemas.cash_flow import CashFlowResponse
from wealthos.modules.dashboard.schemas.category_spending import CategorySpendingResponse
from wealthos.modules.dashboard.schemas.filters import DashboardPeriodParams
from wealthos.modules.dashboard.schemas.recent_transactions import (
    RecentTransactionsResponse,
)
from wealthos.modules.dashboard.schemas.summary import DashboardSummaryResponse
from wealthos.modules.debts.application.queries.get_debt_summary import (
    GetDebtSummaryQuery,
)
from wealthos.modules.debts.schemas.summary import DebtSummaryResponse
from wealthos.modules.goals.application.queries.get_goals_dashboard_summary import (
    GetGoalsDashboardSummaryQuery,
)
from wealthos.modules.goals.schemas.response import GoalsDashboardResponse

router = APIRouter()


def parse_period_params(
    period: Annotated[
        Literal["this_month", "last_month", "last_30_days", "this_year", "custom"],
        Query(),
    ] = "this_month",
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
) -> DashboardPeriodParams:
    try:
        return DashboardPeriodParams(period=period, date_from=date_from, date_to=date_to)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


def _period_filters(params: DashboardPeriodParams) -> DashboardPeriodFilters:
    return DashboardPeriodFilters(
        period=DashboardPeriod(params.period),
        date_from=params.date_from,
        date_to=params.date_to,
    )


@router.get(
    "/{organization_id}/dashboard/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard financial summary",
)
def get_summary(
    organization_id: UUID,
    access: OrganizationAccess,
    query: Annotated[GetDashboardSummaryQuery, Depends(get_summary_query)],
    goals_query: Annotated[
        GetGoalsDashboardSummaryQuery, Depends(get_goals_dashboard_query)
    ],
    debts_query: Annotated[GetDebtSummaryQuery, Depends(get_debts_dashboard_query)],
    params: Annotated[DashboardPeriodParams, Depends(parse_period_params)],
) -> DashboardSummaryResponse:
    summary, date_range = query.execute(
        organization_id,
        timezone=access.timezone,
        primary_currency=access.currency,
        filters=_period_filters(params),
    )
    goals = goals_query.execute(
        organization_id,
        currency=access.currency,
    )
    debts_summary = debts_query.execute(organization_id)
    primary_currency_debts = next(
        (item for item in debts_summary.by_currency if item.currency == access.currency),
        None,
    )
    return DashboardSummaryResponse.from_view(
        summary,
        date_range,
        goals_active=goals.active_goals,
        goals_completed=goals.completed_goals,
        debts_total=(
            primary_currency_debts.total_debt if primary_currency_debts else Decimal("0.00")
        ),
        debts_minimum_payments=(
            primary_currency_debts.total_minimum_payments
            if primary_currency_debts
            else Decimal("0.00")
        ),
        debts_active_count=(
            primary_currency_debts.active_debt_count if primary_currency_debts else 0
        ),
    )


@router.get(
    "/{organization_id}/dashboard/cash-flow",
    response_model=CashFlowResponse,
    summary="Dashboard cash-flow series",
)
def get_cash_flow(
    organization_id: UUID,
    access: OrganizationAccess,
    query: Annotated[GetCashFlowQuery, Depends(get_cash_flow_query)],
    params: Annotated[DashboardPeriodParams, Depends(parse_period_params)],
    granularity: Annotated[
        str,
        Query(pattern="^(day|week|month)$"),
    ] = "day",
) -> CashFlowResponse:
    series, _, gran = query.execute(
        organization_id,
        timezone=access.timezone,
        primary_currency=access.currency,
        filters=_period_filters(params),
        granularity=granularity,
    )
    return CashFlowResponse.from_views(series, gran.value)


@router.get(
    "/{organization_id}/dashboard/spending-by-category",
    response_model=CategorySpendingResponse,
    summary="Dashboard spending by category",
)
def get_spending_by_category(
    organization_id: UUID,
    access: OrganizationAccess,
    query: Annotated[GetSpendingByCategoryQuery, Depends(get_spending_query)],
    params: Annotated[DashboardPeriodParams, Depends(parse_period_params)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    group_by: Annotated[str, Query(pattern="^(root|category)$")] = "root",
) -> CategorySpendingResponse:
    series, _ = query.execute(
        organization_id,
        timezone=access.timezone,
        primary_currency=access.currency,
        filters=_period_filters(params),
        limit=limit,
        group_by=group_by,
    )
    return CategorySpendingResponse.from_views(series)


@router.get(
    "/{organization_id}/dashboard/accounts",
    response_model=AccountSummaryResponse,
    summary="Dashboard account balances",
)
def get_accounts(
    organization_id: UUID,
    access: OrganizationAccess,
    query: Annotated[GetAccountSummaryQuery, Depends(get_account_summary_query)],
    include_archived: bool = False,
) -> AccountSummaryResponse:
    groups = query.execute(
        organization_id,
        primary_currency=access.currency,
        include_archived=include_archived,
    )
    return AccountSummaryResponse.from_views(groups)


@router.get(
    "/{organization_id}/dashboard/recent-transactions",
    response_model=RecentTransactionsResponse,
    summary="Dashboard recent transactions",
)
def get_recent_transactions(
    organization_id: UUID,
    access: OrganizationAccess,
    query: Annotated[GetRecentTransactionsQuery, Depends(get_recent_transactions_query)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> RecentTransactionsResponse:
    items = query.execute(organization_id, limit=limit)
    return RecentTransactionsResponse.from_views(items)


@router.get(
    "/{organization_id}/dashboard/goals",
    response_model=GoalsDashboardResponse,
    summary="Dashboard goals overview",
)
def get_dashboard_goals(
    organization_id: UUID,
    access: OrganizationAccess,
    query: Annotated[GetGoalsDashboardSummaryQuery, Depends(get_goals_dashboard_query)],
) -> GoalsDashboardResponse:
    summary = query.execute(organization_id, currency=access.currency)
    return GoalsDashboardResponse.from_summary(summary)


@router.get(
    "/{organization_id}/dashboard/debts",
    response_model=DebtSummaryResponse,
    summary="Dashboard debts overview",
)
def get_dashboard_debts(
    organization_id: UUID,
    _access: OrganizationAccess,
    query: Annotated[GetDebtSummaryQuery, Depends(get_debts_dashboard_query)],
) -> DebtSummaryResponse:
    summary = query.execute(organization_id)
    return DebtSummaryResponse.from_summary(summary)
