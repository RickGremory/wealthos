"""HTTP routes for budgets nested under organizations."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.planning.api.dependencies import (
    get_activate_budget_command,
    get_add_budget_allocation_command,
    get_archive_budget_command,
    get_budget_forecast_query,
    get_budget_performance_query,
    get_close_budget_command,
    get_create_budget_command,
    get_get_budget_query,
    get_list_budgets_query,
    get_match_budget_allocation_command,
    get_remove_budget_allocation_command,
    get_unit_of_work,
    get_update_budget_allocation_command,
    get_update_budget_command,
)
from wealthos.modules.planning.api.exception_mapping import http_map_planning_errors
from wealthos.modules.planning.application.commands.activate_budget import (
    ActivateBudgetCommand,
    ActivateBudgetInput,
)
from wealthos.modules.planning.application.commands.add_budget_allocation import (
    AddBudgetAllocationCommand,
    AddBudgetAllocationInput,
)
from wealthos.modules.planning.application.commands.archive_budget import (
    ArchiveBudgetCommand,
    ArchiveBudgetInput,
)
from wealthos.modules.planning.application.commands.close_budget import (
    CloseBudgetCommand,
    CloseBudgetInput,
)
from wealthos.modules.planning.application.commands.create_budget import (
    CreateBudgetCommand,
    CreateBudgetInput,
)
from wealthos.modules.planning.application.commands.match_budget_allocation import (
    MatchBudgetAllocationCommand,
    MatchBudgetAllocationInput,
)
from wealthos.modules.planning.application.commands.remove_budget_allocation import (
    RemoveBudgetAllocationCommand,
    RemoveBudgetAllocationInput,
)
from wealthos.modules.planning.application.commands.update_budget import (
    UpdateBudgetCommand,
    UpdateBudgetInput,
)
from wealthos.modules.planning.application.commands.update_budget_allocation import (
    UpdateBudgetAllocationCommand,
    UpdateBudgetAllocationInput,
)
from wealthos.modules.planning.application.queries.get_budget import GetBudgetQuery
from wealthos.modules.planning.application.queries.get_budget_forecast import (
    GetBudgetForecastQuery,
)
from wealthos.modules.planning.application.queries.get_budget_performance import (
    GetBudgetPerformanceQuery,
)
from wealthos.modules.planning.application.queries.list_budgets import ListBudgetsQuery
from wealthos.modules.planning.domain.exceptions import PlanningError
from wealthos.modules.planning.schemas.allocation import (
    BudgetAllocationCreate,
    BudgetAllocationMatchCreate,
    BudgetAllocationMatchResponse,
    BudgetAllocationResponse,
    BudgetAllocationUpdate,
)
from wealthos.modules.planning.schemas.budget import (
    BudgetCreate,
    BudgetListResponse,
    BudgetResponse,
    BudgetUpdate,
)
from wealthos.modules.planning.schemas.forecast import BudgetForecastResponse
from wealthos.modules.planning.schemas.performance import BudgetPerformanceResponse
from wealthos.shared.domain.exceptions import InvalidCurrency
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]
RequireManager = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


def _budget_response(detail) -> BudgetResponse:
    return BudgetResponse.from_entity(
        detail.budget,
        allocations=[BudgetAllocationResponse.from_entity(a) for a in detail.allocations],
    )


@router.post(
    "/{organization_id}/budgets",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create budget",
    description=(
        "Creates a **Budget**: a planned income/expense envelope for a period "
        "(monthly/quarterly/annual/custom). Distinct from Cash Plans, which project "
        "dated liquidity movements."
    ),
)
def create_budget(
    organization_id: UUID,
    payload: BudgetCreate,
    _membership: RequireWriter,
    command: Annotated[CreateBudgetCommand, Depends(get_create_budget_command)],
    query: Annotated[GetBudgetQuery, Depends(get_get_budget_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetResponse:
    try:
        with uow:
            budget = command.execute(
                CreateBudgetInput(
                    organization_id=organization_id,
                    name=payload.name,
                    period_type=payload.period_type,
                    currency=payload.currency.upper(),
                    rollover_policy=payload.rollover_policy,
                    forecast_method=payload.forecast_method,
                    reference_date=payload.reference_date,
                    date_from=payload.date_from,
                    date_to=payload.date_to,
                )
            )
            uow.commit()
    except (PlanningError, InvalidCurrency) as exc:
        raise http_map_planning_errors(exc) from exc

    return _budget_response(query.execute(organization_id, budget.id))


@router.get(
    "/{organization_id}/budgets",
    response_model=BudgetListResponse,
    summary="List budgets",
)
def list_budgets(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListBudgetsQuery, Depends(get_list_budgets_query)],
    status_filter: Annotated[
        str | None,
        Query(alias="status", pattern="^(draft|active|closed|archived)$"),
    ] = None,
    currency: str | None = None,
    include_archived: bool = Query(default=False),
) -> BudgetListResponse:
    items = query.execute(
        organization_id,
        status=status_filter,
        currency=currency.upper() if currency else None,
        include_archived=include_archived,
    )
    return BudgetListResponse(
        items=[BudgetResponse.from_entity(item) for item in items],
        total=len(items),
    )


@router.get(
    "/{organization_id}/budgets/{budget_id}",
    response_model=BudgetResponse,
    summary="Get budget",
)
def get_budget(
    organization_id: UUID,
    budget_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetBudgetQuery, Depends(get_get_budget_query)],
) -> BudgetResponse:
    try:
        detail = query.execute(organization_id, budget_id)
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _budget_response(detail)


@router.patch(
    "/{organization_id}/budgets/{budget_id}",
    response_model=BudgetResponse,
    summary="Update budget",
)
def update_budget(
    organization_id: UUID,
    budget_id: UUID,
    payload: BudgetUpdate,
    _membership: RequireWriter,
    command: Annotated[UpdateBudgetCommand, Depends(get_update_budget_command)],
    query: Annotated[GetBudgetQuery, Depends(get_get_budget_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetResponse:
    try:
        with uow:
            command.execute(
                UpdateBudgetInput(
                    organization_id=organization_id,
                    budget_id=budget_id,
                    name=payload.name,
                    date_from=payload.date_from,
                    date_to=payload.date_to,
                    rollover_policy=payload.rollover_policy,
                    forecast_method=payload.forecast_method,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _budget_response(query.execute(organization_id, budget_id))


@router.post(
    "/{organization_id}/budgets/{budget_id}/activate",
    response_model=BudgetResponse,
    summary="Activate budget",
)
def activate_budget(
    organization_id: UUID,
    budget_id: UUID,
    _membership: RequireWriter,
    command: Annotated[ActivateBudgetCommand, Depends(get_activate_budget_command)],
    query: Annotated[GetBudgetQuery, Depends(get_get_budget_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetResponse:
    try:
        with uow:
            command.execute(
                ActivateBudgetInput(organization_id=organization_id, budget_id=budget_id)
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _budget_response(query.execute(organization_id, budget_id))


@router.post(
    "/{organization_id}/budgets/{budget_id}/close",
    response_model=BudgetResponse,
    summary="Close budget",
)
def close_budget(
    organization_id: UUID,
    budget_id: UUID,
    _membership: RequireManager,
    command: Annotated[CloseBudgetCommand, Depends(get_close_budget_command)],
    query: Annotated[GetBudgetQuery, Depends(get_get_budget_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetResponse:
    try:
        with uow:
            command.execute(CloseBudgetInput(organization_id=organization_id, budget_id=budget_id))
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _budget_response(query.execute(organization_id, budget_id))


@router.post(
    "/{organization_id}/budgets/{budget_id}/archive",
    response_model=BudgetResponse,
    summary="Archive budget",
)
def archive_budget(
    organization_id: UUID,
    budget_id: UUID,
    _membership: RequireManager,
    command: Annotated[ArchiveBudgetCommand, Depends(get_archive_budget_command)],
    query: Annotated[GetBudgetQuery, Depends(get_get_budget_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetResponse:
    try:
        with uow:
            command.execute(
                ArchiveBudgetInput(organization_id=organization_id, budget_id=budget_id)
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _budget_response(query.execute(organization_id, budget_id))


@router.post(
    "/{organization_id}/budgets/{budget_id}/allocations",
    response_model=BudgetAllocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add budget allocation",
)
def add_budget_allocation(
    organization_id: UUID,
    budget_id: UUID,
    payload: BudgetAllocationCreate,
    _membership: RequireWriter,
    command: Annotated[AddBudgetAllocationCommand, Depends(get_add_budget_allocation_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetAllocationResponse:
    try:
        with uow:
            allocation = command.execute(
                AddBudgetAllocationInput(
                    organization_id=organization_id,
                    budget_id=budget_id,
                    allocation_type=payload.allocation_type,
                    amount=payload.amount,
                    category_id=payload.category_id,
                    goal_id=payload.goal_id,
                    debt_id=payload.debt_id,
                    tax_profile_id=payload.tax_profile_id,
                    destination_account_id=payload.destination_account_id,
                    notes=payload.notes,
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return BudgetAllocationResponse.from_entity(allocation)


@router.patch(
    "/{organization_id}/budgets/{budget_id}/allocations/{allocation_id}",
    response_model=BudgetAllocationResponse,
    summary="Update budget allocation",
)
def update_budget_allocation(
    organization_id: UUID,
    budget_id: UUID,
    allocation_id: UUID,
    payload: BudgetAllocationUpdate,
    _membership: RequireWriter,
    command: Annotated[
        UpdateBudgetAllocationCommand, Depends(get_update_budget_allocation_command)
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetAllocationResponse:
    try:
        with uow:
            allocation = command.execute(
                UpdateBudgetAllocationInput(
                    organization_id=organization_id,
                    budget_id=budget_id,
                    allocation_id=allocation_id,
                    amount=payload.amount,
                    notes=payload.notes,
                    category_id=payload.category_id,
                    goal_id=payload.goal_id,
                    debt_id=payload.debt_id,
                    tax_profile_id=payload.tax_profile_id,
                    destination_account_id=payload.destination_account_id,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return BudgetAllocationResponse.from_entity(allocation)


@router.delete(
    "/{organization_id}/budgets/{budget_id}/allocations/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove budget allocation",
)
def remove_budget_allocation(
    organization_id: UUID,
    budget_id: UUID,
    allocation_id: UUID,
    _membership: RequireWriter,
    command: Annotated[
        RemoveBudgetAllocationCommand, Depends(get_remove_budget_allocation_command)
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> Response:
    try:
        with uow:
            command.execute(
                RemoveBudgetAllocationInput(
                    organization_id=organization_id,
                    budget_id=budget_id,
                    allocation_id=allocation_id,
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{organization_id}/budgets/{budget_id}/allocations/{allocation_id}/match",
    response_model=BudgetAllocationMatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Match transaction to budget allocation",
)
def match_budget_allocation(
    organization_id: UUID,
    budget_id: UUID,
    allocation_id: UUID,
    payload: BudgetAllocationMatchCreate,
    _membership: RequireWriter,
    command: Annotated[MatchBudgetAllocationCommand, Depends(get_match_budget_allocation_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> BudgetAllocationMatchResponse:
    try:
        with uow:
            match = command.execute(
                MatchBudgetAllocationInput(
                    organization_id=organization_id,
                    budget_id=budget_id,
                    allocation_id=allocation_id,
                    transaction_id=payload.transaction_id,
                    matched_amount=payload.matched_amount,
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return BudgetAllocationMatchResponse.from_entity(match)


@router.get(
    "/{organization_id}/budgets/{budget_id}/performance",
    response_model=BudgetPerformanceResponse,
    summary="Budget performance",
)
def get_budget_performance(
    organization_id: UUID,
    budget_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetBudgetPerformanceQuery, Depends(get_budget_performance_query)],
) -> BudgetPerformanceResponse:
    try:
        result = query.execute(organization_id, budget_id)
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return BudgetPerformanceResponse.from_summary(result.summary, budget=result.budget)


@router.get(
    "/{organization_id}/budgets/{budget_id}/forecast",
    response_model=BudgetForecastResponse,
    summary="Budget forecast",
)
def get_budget_forecast(
    organization_id: UUID,
    budget_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetBudgetForecastQuery, Depends(get_budget_forecast_query)],
) -> BudgetForecastResponse:
    try:
        forecast = query.execute(organization_id, budget_id)
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return BudgetForecastResponse.from_forecast(forecast)
