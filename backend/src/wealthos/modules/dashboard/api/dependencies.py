"""FastAPI dependencies for dashboard."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
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
from wealthos.modules.dashboard.application.services.dashboard_period_resolver import (
    DashboardPeriodResolver,
)
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)
from wealthos.modules.dashboard.infrastructure.repositories import (
    SqlAlchemyDashboardReadRepository,
)
from wealthos.modules.goals.application.queries.get_goals_dashboard_summary import (
    GetGoalsDashboardSummaryQuery,
)
from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.goals.infrastructure.repositories import SqlAlchemyGoalRepository


def get_dashboard_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DashboardReadRepository:
    return SqlAlchemyDashboardReadRepository(session)


def get_period_resolver() -> DashboardPeriodResolver:
    return DashboardPeriodResolver()


def get_summary_query(
    repository: Annotated[DashboardReadRepository, Depends(get_dashboard_repository)],
    resolver: Annotated[DashboardPeriodResolver, Depends(get_period_resolver)],
) -> GetDashboardSummaryQuery:
    return GetDashboardSummaryQuery(repository, resolver)


def get_cash_flow_query(
    repository: Annotated[DashboardReadRepository, Depends(get_dashboard_repository)],
    resolver: Annotated[DashboardPeriodResolver, Depends(get_period_resolver)],
) -> GetCashFlowQuery:
    return GetCashFlowQuery(repository, resolver)


def get_spending_query(
    repository: Annotated[DashboardReadRepository, Depends(get_dashboard_repository)],
    resolver: Annotated[DashboardPeriodResolver, Depends(get_period_resolver)],
) -> GetSpendingByCategoryQuery:
    return GetSpendingByCategoryQuery(repository, resolver)


def get_account_summary_query(
    repository: Annotated[DashboardReadRepository, Depends(get_dashboard_repository)],
) -> GetAccountSummaryQuery:
    return GetAccountSummaryQuery(repository)


def get_recent_transactions_query(
    repository: Annotated[DashboardReadRepository, Depends(get_dashboard_repository)],
) -> GetRecentTransactionsQuery:
    return GetRecentTransactionsQuery(repository)


def get_goal_repository(
    session: Annotated[Session, Depends(get_db)],
) -> GoalRepository:
    return SqlAlchemyGoalRepository(session)


def get_goals_dashboard_query(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
) -> GetGoalsDashboardSummaryQuery:
    return GetGoalsDashboardSummaryQuery(goals, GoalProgressService(goals))
