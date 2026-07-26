"""FastAPI dependencies for the planning module."""

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
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.categories.infrastructure.repositories import (
    SqlAlchemyCategoryRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.infrastructure.repositories import SqlAlchemyDebtRepository
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.goals.infrastructure.repositories import SqlAlchemyGoalRepository
from wealthos.modules.planning.application.commands.accept_cash_plan_suggestions import (
    AcceptCashPlanSuggestionsCommand,
)
from wealthos.modules.planning.application.commands.activate_budget import (
    ActivateBudgetCommand,
)
from wealthos.modules.planning.application.commands.add_budget_allocation import (
    AddBudgetAllocationCommand,
)
from wealthos.modules.planning.application.commands.add_cash_plan_item import (
    AddCashPlanItemCommand,
)
from wealthos.modules.planning.application.commands.archive_budget import (
    ArchiveBudgetCommand,
)
from wealthos.modules.planning.application.commands.archive_cash_plan import (
    ArchiveCashPlanCommand,
)
from wealthos.modules.planning.application.commands.cancel_cash_plan_item import (
    CancelCashPlanItemCommand,
)
from wealthos.modules.planning.application.commands.close_budget import CloseBudgetCommand
from wealthos.modules.planning.application.commands.create_budget import CreateBudgetCommand
from wealthos.modules.planning.application.commands.create_cash_plan import (
    CreateCashPlanCommand,
)
from wealthos.modules.planning.application.commands.generate_cash_plan_suggestions import (
    GenerateCashPlanSuggestionsCommand,
)
from wealthos.modules.planning.application.commands.match_budget_allocation import (
    MatchBudgetAllocationCommand,
)
from wealthos.modules.planning.application.commands.match_cash_plan_item import (
    MatchCashPlanItemCommand,
)
from wealthos.modules.planning.application.commands.remove_budget_allocation import (
    RemoveBudgetAllocationCommand,
)
from wealthos.modules.planning.application.commands.update_budget import UpdateBudgetCommand
from wealthos.modules.planning.application.commands.update_budget_allocation import (
    UpdateBudgetAllocationCommand,
)
from wealthos.modules.planning.application.commands.update_cash_plan import (
    UpdateCashPlanCommand,
)
from wealthos.modules.planning.application.commands.update_cash_plan_item import (
    UpdateCashPlanItemCommand,
)
from wealthos.modules.planning.application.queries.get_budget import GetBudgetQuery
from wealthos.modules.planning.application.queries.get_budget_forecast import (
    GetBudgetForecastQuery,
)
from wealthos.modules.planning.application.queries.get_budget_performance import (
    GetBudgetPerformanceQuery,
)
from wealthos.modules.planning.application.queries.get_cash_plan import GetCashPlanQuery
from wealthos.modules.planning.application.queries.get_cash_plan_alerts import (
    GetCashPlanAlertsQuery,
)
from wealthos.modules.planning.application.queries.get_cash_projection import (
    GetCashProjectionQuery,
)
from wealthos.modules.planning.application.queries.get_planning_summary import (
    GetPlanningSummaryQuery,
)
from wealthos.modules.planning.application.queries.list_budgets import ListBudgetsQuery
from wealthos.modules.planning.application.queries.list_cash_plans import ListCashPlansQuery
from wealthos.modules.planning.application.services.budget_forecast_service import (
    BudgetForecastService,
)
from wealthos.modules.planning.application.services.budget_performance_service import (
    BudgetPerformanceService,
)
from wealthos.modules.planning.application.services.cash_alert_service import CashAlertService
from wealthos.modules.planning.application.services.cash_buffer_service import (
    CashBufferService,
)
from wealthos.modules.planning.application.services.cash_plan_matching_service import (
    CashPlanMatchingService,
)
from wealthos.modules.planning.application.services.cash_projection_service import (
    CashProjectionService,
)
from wealthos.modules.planning.application.services.safe_to_spend_service import (
    SafeToSpendService,
)
from wealthos.modules.planning.domain.repositories.budget_allocation_match_repository import (
    BudgetAllocationMatchRepository,
)
from wealthos.modules.planning.domain.repositories.budget_allocation_repository import (
    BudgetAllocationRepository,
)
from wealthos.modules.planning.domain.repositories.budget_repository import BudgetRepository
from wealthos.modules.planning.domain.repositories.cash_plan_item_match_repository import (
    CashPlanItemMatchRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)
from wealthos.modules.planning.domain.repositories.planning_read_repository import (
    PlanningReadRepository,
)
from wealthos.modules.planning.infrastructure.repositories import (
    SqlAlchemyBudgetAllocationMatchRepository,
    SqlAlchemyBudgetAllocationRepository,
    SqlAlchemyBudgetRepository,
    SqlAlchemyCashPlanItemMatchRepository,
    SqlAlchemyCashPlanItemRepository,
    SqlAlchemyCashPlanRepository,
    SqlAlchemyPlanningReadRepository,
)
from wealthos.modules.taxes.api.dependencies import get_tax_summary_query
from wealthos.modules.taxes.application.queries.get_tax_summary import GetTaxSummaryQuery
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.infrastructure.repositories import (
    SqlAlchemyTaxProfileRepository,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from wealthos.modules.transactions.infrastructure.repositories import (
    SqlAlchemyTransactionRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_budget_repository(
    session: Annotated[Session, Depends(get_db)],
) -> BudgetRepository:
    return SqlAlchemyBudgetRepository(session)


def get_budget_allocation_repository(
    session: Annotated[Session, Depends(get_db)],
) -> BudgetAllocationRepository:
    return SqlAlchemyBudgetAllocationRepository(session)


def get_budget_allocation_match_repository(
    session: Annotated[Session, Depends(get_db)],
) -> BudgetAllocationMatchRepository:
    return SqlAlchemyBudgetAllocationMatchRepository(session)


def get_cash_plan_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CashPlanRepository:
    return SqlAlchemyCashPlanRepository(session)


def get_cash_plan_item_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CashPlanItemRepository:
    return SqlAlchemyCashPlanItemRepository(session)


def get_cash_plan_item_match_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CashPlanItemMatchRepository:
    return SqlAlchemyCashPlanItemMatchRepository(session)


def get_planning_read_repository(
    session: Annotated[Session, Depends(get_db)],
) -> PlanningReadRepository:
    return SqlAlchemyPlanningReadRepository(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_category_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def get_goal_repository(
    session: Annotated[Session, Depends(get_db)],
) -> GoalRepository:
    return SqlAlchemyGoalRepository(session)


def get_debt_repository(
    session: Annotated[Session, Depends(get_db)],
) -> DebtRepository:
    return SqlAlchemyDebtRepository(session)


def get_tax_profile_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TaxProfileRepository:
    return SqlAlchemyTaxProfileRepository(session)


def get_transaction_repository(
    session: Annotated[Session, Depends(get_db)],
) -> TransactionRepository:
    return SqlAlchemyTransactionRepository(session)


def get_matching_service() -> CashPlanMatchingService:
    return CashPlanMatchingService()


def get_performance_service() -> BudgetPerformanceService:
    return BudgetPerformanceService()


def get_forecast_service() -> BudgetForecastService:
    return BudgetForecastService()


def get_projection_service() -> CashProjectionService:
    return CashProjectionService()


def get_buffer_service() -> CashBufferService:
    return CashBufferService()


def get_safe_to_spend_service() -> SafeToSpendService:
    return SafeToSpendService()


def get_alert_service() -> CashAlertService:
    return CashAlertService()


def get_create_budget_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> CreateBudgetCommand:
    return CreateBudgetCommand(budgets)


def get_update_budget_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> UpdateBudgetCommand:
    return UpdateBudgetCommand(budgets)


def get_activate_budget_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> ActivateBudgetCommand:
    return ActivateBudgetCommand(budgets)


def get_close_budget_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> CloseBudgetCommand:
    return CloseBudgetCommand(budgets)


def get_archive_budget_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> ArchiveBudgetCommand:
    return ArchiveBudgetCommand(budgets)


def get_add_budget_allocation_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    tax_profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
) -> AddBudgetAllocationCommand:
    return AddBudgetAllocationCommand(
        budgets, allocations, accounts, categories, goals, debts, tax_profiles
    )


def get_update_budget_allocation_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    tax_profiles: Annotated[TaxProfileRepository, Depends(get_tax_profile_repository)],
) -> UpdateBudgetAllocationCommand:
    return UpdateBudgetAllocationCommand(
        budgets, allocations, accounts, categories, goals, debts, tax_profiles
    )


def get_remove_budget_allocation_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
) -> RemoveBudgetAllocationCommand:
    return RemoveBudgetAllocationCommand(budgets, allocations)


def get_match_budget_allocation_command(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
    matches: Annotated[
        BudgetAllocationMatchRepository, Depends(get_budget_allocation_match_repository)
    ],
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    matching: Annotated[CashPlanMatchingService, Depends(get_matching_service)],
) -> MatchBudgetAllocationCommand:
    return MatchBudgetAllocationCommand(budgets, allocations, matches, transactions, matching)


def get_create_cash_plan_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateCashPlanCommand:
    return CreateCashPlanCommand(cash_plans, accounts)


def get_update_cash_plan_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> UpdateCashPlanCommand:
    return UpdateCashPlanCommand(cash_plans, accounts)


def get_archive_cash_plan_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
) -> ArchiveCashPlanCommand:
    return ArchiveCashPlanCommand(cash_plans)


def get_add_cash_plan_item_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
) -> AddCashPlanItemCommand:
    return AddCashPlanItemCommand(cash_plans, items, accounts, categories, goals, debts)


def get_update_cash_plan_item_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    categories: Annotated[CategoryRepository, Depends(get_category_repository)],
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
) -> UpdateCashPlanItemCommand:
    return UpdateCashPlanItemCommand(cash_plans, items, accounts, categories, goals, debts)


def get_cancel_cash_plan_item_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
) -> CancelCashPlanItemCommand:
    return CancelCashPlanItemCommand(cash_plans, items)


def get_match_cash_plan_item_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
    matches: Annotated[CashPlanItemMatchRepository, Depends(get_cash_plan_item_match_repository)],
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    matching: Annotated[CashPlanMatchingService, Depends(get_matching_service)],
) -> MatchCashPlanItemCommand:
    return MatchCashPlanItemCommand(cash_plans, items, matches, transactions, matching)


def get_generate_cash_plan_suggestions_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    tax_summary: Annotated[GetTaxSummaryQuery, Depends(get_tax_summary_query)],
) -> GenerateCashPlanSuggestionsCommand:
    return GenerateCashPlanSuggestionsCommand(cash_plans, debts, tax_summary)


def get_accept_cash_plan_suggestions_command(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
) -> AcceptCashPlanSuggestionsCommand:
    return AcceptCashPlanSuggestionsCommand(cash_plans, items)


def get_get_budget_query(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
) -> GetBudgetQuery:
    return GetBudgetQuery(budgets, allocations)


def get_list_budgets_query(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
) -> ListBudgetsQuery:
    return ListBudgetsQuery(budgets)


def get_budget_performance_query(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
    read: Annotated[PlanningReadRepository, Depends(get_planning_read_repository)],
    performance: Annotated[BudgetPerformanceService, Depends(get_performance_service)],
) -> GetBudgetPerformanceQuery:
    return GetBudgetPerformanceQuery(budgets, allocations, read, performance)


def get_budget_forecast_query(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    allocations: Annotated[BudgetAllocationRepository, Depends(get_budget_allocation_repository)],
    read: Annotated[PlanningReadRepository, Depends(get_planning_read_repository)],
    forecast: Annotated[BudgetForecastService, Depends(get_forecast_service)],
) -> GetBudgetForecastQuery:
    return GetBudgetForecastQuery(budgets, allocations, read, forecast)


def get_get_cash_plan_query(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
) -> GetCashPlanQuery:
    return GetCashPlanQuery(cash_plans, items)


def get_list_cash_plans_query(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
) -> ListCashPlansQuery:
    return ListCashPlansQuery(cash_plans)


def get_cash_projection_query(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
    matches: Annotated[CashPlanItemMatchRepository, Depends(get_cash_plan_item_match_repository)],
    read: Annotated[PlanningReadRepository, Depends(get_planning_read_repository)],
    projection: Annotated[CashProjectionService, Depends(get_projection_service)],
    buffer: Annotated[CashBufferService, Depends(get_buffer_service)],
    safe: Annotated[SafeToSpendService, Depends(get_safe_to_spend_service)],
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
) -> GetCashProjectionQuery:
    return GetCashProjectionQuery(
        cash_plans,
        items,
        matches,
        read,
        projection,
        buffer,
        safe,
        transactions=transactions,
    )


def get_cash_plan_alerts_query(
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    items: Annotated[CashPlanItemRepository, Depends(get_cash_plan_item_repository)],
    read: Annotated[PlanningReadRepository, Depends(get_planning_read_repository)],
    projection_query: Annotated[GetCashProjectionQuery, Depends(get_cash_projection_query)],
    alerts: Annotated[CashAlertService, Depends(get_alert_service)],
    buffer: Annotated[CashBufferService, Depends(get_buffer_service)],
) -> GetCashPlanAlertsQuery:
    return GetCashPlanAlertsQuery(cash_plans, items, read, projection_query, alerts, buffer)


def get_planning_summary_query(
    budgets: Annotated[BudgetRepository, Depends(get_budget_repository)],
    cash_plans: Annotated[CashPlanRepository, Depends(get_cash_plan_repository)],
    projection_query: Annotated[GetCashProjectionQuery, Depends(get_cash_projection_query)],
) -> GetPlanningSummaryQuery:
    return GetPlanningSummaryQuery(budgets, cash_plans, projection_query)


# --- SPEC-004 projection spine -------------------------------------------------

from wealthos.modules.organizations.api.dependencies import get_organization_repository
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)
from wealthos.modules.planning.application.commands.cancel_planned_cash_flow import (
    CancelPlannedCashFlowCommand,
)
from wealthos.modules.planning.application.commands.create_planned_cash_flow import (
    CreatePlannedCashFlowCommand,
)
from wealthos.modules.planning.application.commands.update_planned_cash_flow import (
    UpdatePlannedCashFlowCommand,
)
from wealthos.modules.planning.application.commands.update_planning_settings import (
    UpdatePlanningSettingsCommand,
)
from wealthos.modules.planning.application.queries.get_planning_projection import (
    GetPlanningProjectionQuery,
    GetSafeToSpendSummaryQuery,
)
from wealthos.modules.planning.application.queries.get_planning_settings import (
    GetPlanningSettingsQuery,
)
from wealthos.modules.planning.application.queries.get_planning_sources import (
    GetPlanningSourcesQuery,
)
from wealthos.modules.planning.application.queries.list_planned_cash_flows import (
    ListPlannedCashFlowsQuery,
)
from wealthos.modules.planning.application.queries.simulate_planning_scenario import (
    SimulatePlanningScenarioQuery,
)
from wealthos.modules.planning.domain.ports.repositories import (
    PlannedCashFlowRepository,
    PlanningSettingsRepository,
)
from wealthos.modules.planning.domain.services.context_builder import PlanningContextBuilder
from wealthos.modules.planning.infrastructure.adapters import (
    AccountsPlanningAdapter,
    CommitmentsPlanningAdapter,
    GoalsPlanningAdapter,
    ManualPlanningAdapter,
    RecurringPlanningAdapter,
    TaxesPlanningAdapter,
    TransactionsPlanningAdapter,
)
from wealthos.modules.planning.infrastructure.repositories import (
    SqlAlchemyPlannedCashFlowRepository,
    SqlAlchemyPlanningSettingsRepository,
)


def get_planning_settings_repository(
    session: Annotated[Session, Depends(get_db)],
) -> PlanningSettingsRepository:
    return SqlAlchemyPlanningSettingsRepository(session)


def get_planned_cash_flow_repository(
    session: Annotated[Session, Depends(get_db)],
) -> PlannedCashFlowRepository:
    return SqlAlchemyPlannedCashFlowRepository(session)


def get_planning_context_builder(
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
    debts: Annotated[DebtRepository, Depends(get_debt_repository)],
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    planned: Annotated[PlannedCashFlowRepository, Depends(get_planned_cash_flow_repository)],
    transactions: Annotated[TransactionRepository, Depends(get_transaction_repository)],
) -> PlanningContextBuilder:
    return PlanningContextBuilder(
        [
            AccountsPlanningAdapter(accounts),
            TransactionsPlanningAdapter(transactions),
            CommitmentsPlanningAdapter(debts, accounts),
            GoalsPlanningAdapter(goals),
            TaxesPlanningAdapter(),
            RecurringPlanningAdapter(),
            ManualPlanningAdapter(planned),
        ]
    )


def get_get_planning_projection_query(
    organizations: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    settings: Annotated[PlanningSettingsRepository, Depends(get_planning_settings_repository)],
    context_builder: Annotated[PlanningContextBuilder, Depends(get_planning_context_builder)],
) -> GetPlanningProjectionQuery:
    return GetPlanningProjectionQuery(organizations, settings, context_builder)


def get_get_safe_to_spend_summary_query(
    projection: Annotated[GetPlanningProjectionQuery, Depends(get_get_planning_projection_query)],
) -> GetSafeToSpendSummaryQuery:
    return GetSafeToSpendSummaryQuery(projection)


def get_get_planning_sources_query(
    projection: Annotated[GetPlanningProjectionQuery, Depends(get_get_planning_projection_query)],
) -> GetPlanningSourcesQuery:
    return GetPlanningSourcesQuery(projection)


def get_get_planning_settings_query(
    settings: Annotated[PlanningSettingsRepository, Depends(get_planning_settings_repository)],
) -> GetPlanningSettingsQuery:
    return GetPlanningSettingsQuery(settings)


def get_list_planned_cash_flows_query(
    planned: Annotated[PlannedCashFlowRepository, Depends(get_planned_cash_flow_repository)],
) -> ListPlannedCashFlowsQuery:
    return ListPlannedCashFlowsQuery(planned)


def get_simulate_planning_scenario_query(
    projection: Annotated[GetPlanningProjectionQuery, Depends(get_get_planning_projection_query)],
) -> SimulatePlanningScenarioQuery:
    return SimulatePlanningScenarioQuery(projection)


def get_create_planned_cash_flow_command(
    planned: Annotated[PlannedCashFlowRepository, Depends(get_planned_cash_flow_repository)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CreatePlannedCashFlowCommand:
    return CreatePlannedCashFlowCommand(planned, uow)


def get_update_planned_cash_flow_command(
    planned: Annotated[PlannedCashFlowRepository, Depends(get_planned_cash_flow_repository)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> UpdatePlannedCashFlowCommand:
    return UpdatePlannedCashFlowCommand(planned, uow)


def get_cancel_planned_cash_flow_command(
    planned: Annotated[PlannedCashFlowRepository, Depends(get_planned_cash_flow_repository)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CancelPlannedCashFlowCommand:
    return CancelPlannedCashFlowCommand(planned, uow)


def get_update_planning_settings_command(
    settings: Annotated[PlanningSettingsRepository, Depends(get_planning_settings_repository)],
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> UpdatePlanningSettingsCommand:
    return UpdatePlanningSettingsCommand(settings, goals, uow)
