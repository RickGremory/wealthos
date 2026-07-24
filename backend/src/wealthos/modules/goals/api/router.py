"""HTTP routes for goals nested under organizations."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.goals.api.dependencies import (
    get_archive_goal_command,
    get_create_goal_command,
    get_get_goal_query,
    get_list_goals_query,
    get_manual_progress_command,
    get_progress_service,
    get_unit_of_work,
    get_update_goal_command,
)
from wealthos.modules.goals.application.commands.archive_goal import (
    ArchiveGoalCommand,
    ArchiveGoalInput,
)
from wealthos.modules.goals.application.commands.create_goal import (
    CreateGoalCommand,
    CreateGoalInput,
)
from wealthos.modules.goals.application.commands.update_goal import (
    UpdateGoalCommand,
    UpdateGoalInput,
)
from wealthos.modules.goals.application.commands.update_manual_progress import (
    UpdateManualProgressCommand,
    UpdateManualProgressInput,
)
from wealthos.modules.goals.application.queries.get_goal import (
    GetGoalQuery,
    GoalWithProgress,
    ListGoalsQuery,
)
from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.exceptions import (
    GoalAccountNotFound,
    GoalAlreadyArchived,
    GoalError,
    GoalNameEmpty,
    GoalNameTooLong,
    GoalNotFoundError,
    InvalidGoalStrategy,
    InvalidTargetAmount,
)
from wealthos.modules.goals.schemas.create import (
    GoalCreate,
    GoalUpdate,
    ManualProgressUpdate,
)
from wealthos.modules.goals.schemas.response import GoalListResponse, GoalResponse
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.shared.domain.exceptions import InvalidCurrency
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]
RequireArchiver = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


def _http_map_goal_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, (GoalNotFoundError, GoalAccountNotFound)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(
        exc,
        GoalNameEmpty
        | GoalNameTooLong
        | InvalidGoalStrategy
        | InvalidTargetAmount
        | InvalidCurrency,
    ):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    if isinstance(exc, GoalAlreadyArchived):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, GoalError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/{organization_id}/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create goal",
)
def create_goal(
    organization_id: UUID,
    payload: GoalCreate,
    _membership: RequireWriter,
    command: Annotated[CreateGoalCommand, Depends(get_create_goal_command)],
    progress_service: Annotated[GoalProgressService, Depends(get_progress_service)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> GoalResponse:
    try:
        with uow:
            goal = command.execute(
                CreateGoalInput(
                    organization_id=organization_id,
                    name=payload.name,
                    target_amount=payload.target_amount,
                    currency=payload.currency.upper(),
                    strategy=payload.strategy,
                    target_date=payload.target_date,
                    linked_account_ids=tuple(payload.linked_account_ids),
                )
            )
            progress = progress_service.calculate(goal)
            uow.commit()
    except GoalError as exc:
        raise _http_map_goal_errors(exc) from exc
    except InvalidCurrency as exc:
        raise _http_map_goal_errors(exc) from exc

    return GoalResponse.from_goal_with_progress(GoalWithProgress(goal=goal, progress=progress))


@router.get(
    "/{organization_id}/goals",
    response_model=GoalListResponse,
    summary="List goals",
)
def list_goals(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListGoalsQuery, Depends(get_list_goals_query)],
    include_archived: bool = Query(default=False),
) -> GoalListResponse:
    items = query.execute(organization_id, include_archived=include_archived)
    return GoalListResponse(
        items=[GoalResponse.from_goal_with_progress(item) for item in items],
        total=len(items),
    )


@router.get(
    "/{organization_id}/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Get goal",
)
def get_goal(
    organization_id: UUID,
    goal_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetGoalQuery, Depends(get_get_goal_query)],
) -> GoalResponse:
    try:
        item = query.execute(organization_id, goal_id)
    except GoalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return GoalResponse.from_goal_with_progress(item)


@router.patch(
    "/{organization_id}/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Update goal metadata",
)
def update_goal(
    organization_id: UUID,
    goal_id: UUID,
    payload: GoalUpdate,
    _membership: RequireWriter,
    command: Annotated[UpdateGoalCommand, Depends(get_update_goal_command)],
    progress_service: Annotated[GoalProgressService, Depends(get_progress_service)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> GoalResponse:
    try:
        with uow:
            goal = command.execute(
                UpdateGoalInput(
                    organization_id=organization_id,
                    goal_id=goal_id,
                    name=payload.name,
                    target_amount=payload.target_amount,
                    target_date=payload.target_date,
                    linked_account_ids=(
                        tuple(payload.linked_account_ids)
                        if payload.linked_account_ids is not None
                        else None
                    ),
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            progress = progress_service.calculate(goal)
            uow.commit()
    except GoalError as exc:
        raise _http_map_goal_errors(exc) from exc

    return GoalResponse.from_goal_with_progress(GoalWithProgress(goal=goal, progress=progress))


@router.post(
    "/{organization_id}/goals/{goal_id}/archive",
    response_model=GoalResponse,
    summary="Archive goal",
)
def archive_goal(
    organization_id: UUID,
    goal_id: UUID,
    _membership: RequireArchiver,
    command: Annotated[ArchiveGoalCommand, Depends(get_archive_goal_command)],
    progress_service: Annotated[GoalProgressService, Depends(get_progress_service)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> GoalResponse:
    try:
        with uow:
            goal = command.execute(
                ArchiveGoalInput(organization_id=organization_id, goal_id=goal_id)
            )
            progress = progress_service.calculate(goal)
            uow.commit()
    except GoalError as exc:
        raise _http_map_goal_errors(exc) from exc

    return GoalResponse.from_goal_with_progress(GoalWithProgress(goal=goal, progress=progress))


@router.post(
    "/{organization_id}/goals/{goal_id}/manual-progress",
    response_model=GoalResponse,
    summary="Update manual goal progress",
)
def update_manual_progress(
    organization_id: UUID,
    goal_id: UUID,
    payload: ManualProgressUpdate,
    _membership: RequireWriter,
    command: Annotated[UpdateManualProgressCommand, Depends(get_manual_progress_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> GoalResponse:
    try:
        with uow:
            result = command.execute(
                UpdateManualProgressInput(
                    organization_id=organization_id,
                    goal_id=goal_id,
                    current_amount=payload.current_amount,
                )
            )
            uow.commit()
    except GoalError as exc:
        raise _http_map_goal_errors(exc) from exc

    return GoalResponse.from_goal_with_progress(
        GoalWithProgress(goal=result.goal, progress=result.progress)
    )
