"""FastAPI dependencies for goals."""

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
from wealthos.modules.goals.application.commands.archive_goal import ArchiveGoalCommand
from wealthos.modules.goals.application.commands.create_goal import CreateGoalCommand
from wealthos.modules.goals.application.commands.update_goal import UpdateGoalCommand
from wealthos.modules.goals.application.commands.update_manual_progress import (
    UpdateManualProgressCommand,
)
from wealthos.modules.goals.application.queries.get_goal import (
    GetGoalQuery,
    ListGoalsQuery,
)
from wealthos.modules.goals.application.queries.get_goals_dashboard_summary import (
    GetGoalsDashboardSummaryQuery,
)
from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository
from wealthos.modules.goals.infrastructure.repositories import SqlAlchemyGoalRepository
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_goal_repository(
    session: Annotated[Session, Depends(get_db)],
) -> GoalRepository:
    return SqlAlchemyGoalRepository(session)


def get_account_repository(
    session: Annotated[Session, Depends(get_db)],
) -> AccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_progress_service(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
) -> GoalProgressService:
    return GoalProgressService(goals)


def get_create_goal_command(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> CreateGoalCommand:
    return CreateGoalCommand(goals, accounts)


def get_update_goal_command(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    accounts: Annotated[AccountRepository, Depends(get_account_repository)],
) -> UpdateGoalCommand:
    return UpdateGoalCommand(goals, accounts)


def get_archive_goal_command(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
) -> ArchiveGoalCommand:
    return ArchiveGoalCommand(goals)


def get_manual_progress_command(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    progress: Annotated[GoalProgressService, Depends(get_progress_service)],
) -> UpdateManualProgressCommand:
    return UpdateManualProgressCommand(goals, progress)


def get_get_goal_query(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    progress: Annotated[GoalProgressService, Depends(get_progress_service)],
) -> GetGoalQuery:
    return GetGoalQuery(goals, progress)


def get_list_goals_query(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    progress: Annotated[GoalProgressService, Depends(get_progress_service)],
) -> ListGoalsQuery:
    return ListGoalsQuery(goals, progress)


def get_goals_dashboard_query(
    goals: Annotated[GoalRepository, Depends(get_goal_repository)],
    progress: Annotated[GoalProgressService, Depends(get_progress_service)],
) -> GetGoalsDashboardSummaryQuery:
    return GetGoalsDashboardSummaryQuery(goals, progress)
