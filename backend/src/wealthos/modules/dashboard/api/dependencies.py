"""FastAPI dependencies for dashboard."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.accounts.infrastructure.repositories import (
    SqlAlchemyAccountRepository,
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
from wealthos.modules.dashboard.application.services.dashboard_period_resolver import (
    DashboardPeriodResolver,
)
from wealthos.modules.dashboard.domain.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)
from wealthos.modules.dashboard.infrastructure.repositories import (
    SqlAlchemyDashboardReadRepository,
)
from wealthos.modules.debts.application.queries.get_debt_summary import (
    GetDebtSummaryQuery,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.infrastructure.repositories import SqlAlchemyDebtRepository
from wealthos.modules.goals.application.queries.get_goals_dashboard_summary import (
    GetGoalsDashboardSummaryQuery,
)
from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.goals.infrastructure.repositories import SqlAlchemyGoalRepository
from wealthos.modules.taxes.application.queries.get_tax_summary import GetTaxSummaryQuery
from wealthos.modules.taxes.application.services.tax_period_generator import (
    TaxPeriodGenerator,
)
from wealthos.modules.taxes.infrastructure.repositories import (
    SqlAlchemyTaxCalculationRepository,
    SqlAlchemyTaxPaymentRepository,
    SqlAlchemyTaxPeriodRepository,
    SqlAlchemyTaxProfileRepository,
    SqlAlchemyTaxReadRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_dashboard_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DashboardReadRepository:
    return SqlAlchemyDashboardReadRepository(session)


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


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


def get_debt_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DebtRepository:
    return SqlAlchemyDebtRepository(session)


def get_debts_dashboard_query(
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> GetDebtSummaryQuery:
    return GetDebtSummaryQuery(debts, accounts)


def get_tax_profile_repository(
    session: Annotated[Session, Depends(get_db)],
):
    return SqlAlchemyTaxProfileRepository(session)


def get_tax_period_repository(
    session: Annotated[Session, Depends(get_db)],
):
    return SqlAlchemyTaxPeriodRepository(session)


def get_tax_calculation_repository(
    session: Annotated[Session, Depends(get_db)],
):
    return SqlAlchemyTaxCalculationRepository(session)


def get_tax_payment_repository(
    session: Annotated[Session, Depends(get_db)],
):
    return SqlAlchemyTaxPaymentRepository(session)


def get_tax_read_repository(
    session: Annotated[Session, Depends(get_db)],
):
    return SqlAlchemyTaxReadRepository(session)


def get_tax_period_generator(
    periods: Annotated[SqlAlchemyTaxPeriodRepository, Depends(get_tax_period_repository)],
) -> TaxPeriodGenerator:
    return TaxPeriodGenerator(periods)


def get_taxes_dashboard_query(
    profiles: Annotated[SqlAlchemyTaxProfileRepository, Depends(get_tax_profile_repository)],
    periods: Annotated[SqlAlchemyTaxPeriodRepository, Depends(get_tax_period_repository)],
    calculations: Annotated[
        SqlAlchemyTaxCalculationRepository,
        Depends(get_tax_calculation_repository),
    ],
    payments: Annotated[SqlAlchemyTaxPaymentRepository, Depends(get_tax_payment_repository)],
    read: Annotated[SqlAlchemyTaxReadRepository, Depends(get_tax_read_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    period_generator: Annotated[TaxPeriodGenerator, Depends(get_tax_period_generator)],
) -> GetTaxSummaryQuery:
    return GetTaxSummaryQuery(
        profiles,
        periods,
        calculations,
        payments,
        read,
        accounts,
        period_generator,
    )
