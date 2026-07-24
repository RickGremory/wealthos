"""HTTP routes for cash plans nested under organizations."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.planning.api.dependencies import (
    get_accept_cash_plan_suggestions_command,
    get_add_cash_plan_item_command,
    get_archive_cash_plan_command,
    get_cancel_cash_plan_item_command,
    get_cash_plan_alerts_query,
    get_cash_projection_query,
    get_create_cash_plan_command,
    get_generate_cash_plan_suggestions_command,
    get_get_cash_plan_query,
    get_list_cash_plans_query,
    get_match_cash_plan_item_command,
    get_planning_summary_query,
    get_unit_of_work,
    get_update_cash_plan_command,
    get_update_cash_plan_item_command,
)
from wealthos.modules.planning.api.exception_mapping import http_map_planning_errors
from wealthos.modules.planning.application.commands.accept_cash_plan_suggestions import (
    AcceptCashPlanSuggestionsCommand,
    AcceptCashPlanSuggestionsInput,
    AcceptSuggestionItem,
)
from wealthos.modules.planning.application.commands.add_cash_plan_item import (
    AddCashPlanItemCommand,
    AddCashPlanItemInput,
)
from wealthos.modules.planning.application.commands.archive_cash_plan import (
    ArchiveCashPlanCommand,
    ArchiveCashPlanInput,
)
from wealthos.modules.planning.application.commands.cancel_cash_plan_item import (
    CancelCashPlanItemCommand,
    CancelCashPlanItemInput,
)
from wealthos.modules.planning.application.commands.create_cash_plan import (
    CreateCashPlanCommand,
    CreateCashPlanInput,
)
from wealthos.modules.planning.application.commands.generate_cash_plan_suggestions import (
    GenerateCashPlanSuggestionsCommand,
    GenerateCashPlanSuggestionsInput,
)
from wealthos.modules.planning.application.commands.match_cash_plan_item import (
    MatchCashPlanItemCommand,
    MatchCashPlanItemInput,
)
from wealthos.modules.planning.application.commands.update_cash_plan import (
    UpdateCashPlanCommand,
    UpdateCashPlanInput,
)
from wealthos.modules.planning.application.commands.update_cash_plan_item import (
    UpdateCashPlanItemCommand,
    UpdateCashPlanItemInput,
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
from wealthos.modules.planning.application.queries.list_cash_plans import ListCashPlansQuery
from wealthos.modules.planning.domain.exceptions import PlanningError
from wealthos.modules.planning.schemas.alerts import CashAlertListResponse, CashAlertResponse
from wealthos.modules.planning.schemas.cash_plan import (
    CashPlanCreate,
    CashPlanListResponse,
    CashPlanResponse,
    CashPlanUpdate,
)
from wealthos.modules.planning.schemas.cash_plan_item import (
    AcceptCashPlanSuggestionsRequest,
    CashPlanItemCreate,
    CashPlanItemMatchCreate,
    CashPlanItemMatchResponse,
    CashPlanItemResponse,
    CashPlanItemUpdate,
    CashPlanSuggestionListResponse,
    CashPlanSuggestionResponse,
)
from wealthos.modules.planning.schemas.projection import CashProjectionResponse
from wealthos.modules.planning.schemas.summary import PlanningSummaryResponse
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


def _cash_plan_response(detail) -> CashPlanResponse:
    return CashPlanResponse.from_entity(
        detail.cash_plan,
        account_ids=list(detail.account_ids),
        items=[CashPlanItemResponse.from_entity(item) for item in detail.items],
    )


@router.get(
    "/{organization_id}/planning/summary",
    response_model=PlanningSummaryResponse,
    summary="Planning summary",
    description=(
        "Cross-cutting planning snapshot: active/draft budgets and cash plans, plus "
        "`safe_to_spend` for the primary active cash plan when available. "
        "safe_to_spend is an operational estimate (liquid − committed − tax shortfall − buffer) "
        "and is not advice."
    ),
)
def get_planning_summary(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetPlanningSummaryQuery, Depends(get_planning_summary_query)],
) -> PlanningSummaryResponse:
    try:
        summary = query.execute(organization_id)
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return PlanningSummaryResponse.from_summary(summary)


@router.post(
    "/{organization_id}/cash-plans",
    response_model=CashPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create cash plan",
    description=(
        "Creates a **Cash Plan**: a dated liquidity projection horizon with expected "
        "inflows/outflows. Distinct from Budgets (period envelopes for income/expense "
        "allocations)."
    ),
)
def create_cash_plan(
    organization_id: UUID,
    payload: CashPlanCreate,
    _membership: RequireWriter,
    command: Annotated[CreateCashPlanCommand, Depends(get_create_cash_plan_command)],
    query: Annotated[GetCashPlanQuery, Depends(get_get_cash_plan_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanResponse:
    try:
        with uow:
            plan = command.execute(
                CreateCashPlanInput(
                    organization_id=organization_id,
                    name=payload.name,
                    date_from=payload.date_from,
                    date_to=payload.date_to,
                    currency=payload.currency.upper(),
                    opening_balance_mode=payload.opening_balance_mode,
                    manual_opening_balance=payload.manual_opening_balance,
                    account_ids=tuple(payload.account_ids),
                    minimum_cash_buffer_type=payload.minimum_cash_buffer_type,
                    minimum_cash_buffer_value=payload.minimum_cash_buffer_value,
                )
            )
            uow.commit()
    except (PlanningError, InvalidCurrency) as exc:
        raise http_map_planning_errors(exc) from exc
    return _cash_plan_response(query.execute(organization_id, plan.id))


@router.get(
    "/{organization_id}/cash-plans",
    response_model=CashPlanListResponse,
    summary="List cash plans",
)
def list_cash_plans(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListCashPlansQuery, Depends(get_list_cash_plans_query)],
    status_filter: Annotated[
        str | None,
        Query(alias="status", pattern="^(draft|active|completed|archived)$"),
    ] = None,
    currency: str | None = None,
    include_archived: bool = Query(default=False),
) -> CashPlanListResponse:
    items = query.execute(
        organization_id,
        status=status_filter,
        currency=currency.upper() if currency else None,
        include_archived=include_archived,
    )
    return CashPlanListResponse(
        items=[CashPlanResponse.from_entity(item) for item in items],
        total=len(items),
    )


@router.get(
    "/{organization_id}/cash-plans/{cash_plan_id}",
    response_model=CashPlanResponse,
    summary="Get cash plan",
)
def get_cash_plan(
    organization_id: UUID,
    cash_plan_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetCashPlanQuery, Depends(get_get_cash_plan_query)],
) -> CashPlanResponse:
    try:
        detail = query.execute(organization_id, cash_plan_id)
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _cash_plan_response(detail)


@router.patch(
    "/{organization_id}/cash-plans/{cash_plan_id}",
    response_model=CashPlanResponse,
    summary="Update cash plan",
)
def update_cash_plan(
    organization_id: UUID,
    cash_plan_id: UUID,
    payload: CashPlanUpdate,
    _membership: RequireWriter,
    command: Annotated[UpdateCashPlanCommand, Depends(get_update_cash_plan_command)],
    query: Annotated[GetCashPlanQuery, Depends(get_get_cash_plan_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanResponse:
    try:
        with uow:
            command.execute(
                UpdateCashPlanInput(
                    organization_id=organization_id,
                    cash_plan_id=cash_plan_id,
                    name=payload.name,
                    date_from=payload.date_from,
                    date_to=payload.date_to,
                    opening_balance_mode=payload.opening_balance_mode,
                    manual_opening_balance=payload.manual_opening_balance,
                    account_ids=(
                        tuple(payload.account_ids) if payload.account_ids is not None else None
                    ),
                    minimum_cash_buffer_type=payload.minimum_cash_buffer_type,
                    minimum_cash_buffer_value=payload.minimum_cash_buffer_value,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _cash_plan_response(query.execute(organization_id, cash_plan_id))


@router.post(
    "/{organization_id}/cash-plans/{cash_plan_id}/archive",
    response_model=CashPlanResponse,
    summary="Archive cash plan",
)
def archive_cash_plan(
    organization_id: UUID,
    cash_plan_id: UUID,
    _membership: RequireManager,
    command: Annotated[ArchiveCashPlanCommand, Depends(get_archive_cash_plan_command)],
    query: Annotated[GetCashPlanQuery, Depends(get_get_cash_plan_query)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanResponse:
    try:
        with uow:
            command.execute(
                ArchiveCashPlanInput(organization_id=organization_id, cash_plan_id=cash_plan_id)
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return _cash_plan_response(query.execute(organization_id, cash_plan_id))


@router.post(
    "/{organization_id}/cash-plans/{cash_plan_id}/items",
    response_model=CashPlanItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add cash plan item",
)
def add_cash_plan_item(
    organization_id: UUID,
    cash_plan_id: UUID,
    payload: CashPlanItemCreate,
    _membership: RequireWriter,
    command: Annotated[AddCashPlanItemCommand, Depends(get_add_cash_plan_item_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanItemResponse:
    try:
        with uow:
            item = command.execute(
                AddCashPlanItemInput(
                    organization_id=organization_id,
                    cash_plan_id=cash_plan_id,
                    item_type=payload.item_type,
                    description=payload.description,
                    expected_date=payload.expected_date,
                    amount=payload.amount,
                    probability=payload.probability,
                    category_id=payload.category_id,
                    account_id=payload.account_id,
                    linked_entity_type=payload.linked_entity_type,
                    linked_entity_id=payload.linked_entity_id,
                    recurrence_rule=payload.recurrence_rule,
                    notes=payload.notes,
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return CashPlanItemResponse.from_entity(item)


@router.patch(
    "/{organization_id}/cash-plans/{cash_plan_id}/items/{item_id}",
    response_model=CashPlanItemResponse,
    summary="Update cash plan item",
)
def update_cash_plan_item(
    organization_id: UUID,
    cash_plan_id: UUID,
    item_id: UUID,
    payload: CashPlanItemUpdate,
    _membership: RequireWriter,
    command: Annotated[UpdateCashPlanItemCommand, Depends(get_update_cash_plan_item_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanItemResponse:
    try:
        with uow:
            item = command.execute(
                UpdateCashPlanItemInput(
                    organization_id=organization_id,
                    cash_plan_id=cash_plan_id,
                    item_id=item_id,
                    description=payload.description,
                    expected_date=payload.expected_date,
                    amount=payload.amount,
                    probability=payload.probability,
                    category_id=payload.category_id,
                    account_id=payload.account_id,
                    linked_entity_type=payload.linked_entity_type,
                    linked_entity_id=payload.linked_entity_id,
                    recurrence_rule=payload.recurrence_rule,
                    notes=payload.notes,
                    status=payload.status,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return CashPlanItemResponse.from_entity(item)


@router.delete(
    "/{organization_id}/cash-plans/{cash_plan_id}/items/{item_id}",
    response_model=CashPlanItemResponse,
    summary="Cancel cash plan item",
)
def cancel_cash_plan_item(
    organization_id: UUID,
    cash_plan_id: UUID,
    item_id: UUID,
    _membership: RequireWriter,
    command: Annotated[CancelCashPlanItemCommand, Depends(get_cancel_cash_plan_item_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanItemResponse:
    try:
        with uow:
            item = command.execute(
                CancelCashPlanItemInput(
                    organization_id=organization_id,
                    cash_plan_id=cash_plan_id,
                    item_id=item_id,
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return CashPlanItemResponse.from_entity(item)


@router.post(
    "/{organization_id}/cash-plans/{cash_plan_id}/items/{item_id}/match",
    response_model=CashPlanItemMatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Match transaction to cash plan item",
)
def match_cash_plan_item(
    organization_id: UUID,
    cash_plan_id: UUID,
    item_id: UUID,
    payload: CashPlanItemMatchCreate,
    _membership: RequireWriter,
    command: Annotated[MatchCashPlanItemCommand, Depends(get_match_cash_plan_item_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CashPlanItemMatchResponse:
    try:
        with uow:
            match = command.execute(
                MatchCashPlanItemInput(
                    organization_id=organization_id,
                    cash_plan_id=cash_plan_id,
                    item_id=item_id,
                    transaction_id=payload.transaction_id,
                    matched_amount=payload.matched_amount,
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return CashPlanItemMatchResponse.from_entity(match)


@router.post(
    "/{organization_id}/cash-plans/{cash_plan_id}/suggestions/generate",
    response_model=CashPlanSuggestionListResponse,
    summary="Generate cash plan suggestions",
    description=(
        "Returns suggestion DTOs from active debts (payment_day) and tax balance due. "
        "Does not persist; use `/suggestions/accept` to create items."
    ),
)
def generate_cash_plan_suggestions(
    organization_id: UUID,
    cash_plan_id: UUID,
    _membership: RequireWriter,
    command: Annotated[
        GenerateCashPlanSuggestionsCommand, Depends(get_generate_cash_plan_suggestions_command)
    ],
) -> CashPlanSuggestionListResponse:
    try:
        suggestions = command.execute(
            GenerateCashPlanSuggestionsInput(
                organization_id=organization_id, cash_plan_id=cash_plan_id
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    items = [CashPlanSuggestionResponse.from_suggestion(s) for s in suggestions]
    return CashPlanSuggestionListResponse(items=items, total=len(items))


@router.post(
    "/{organization_id}/cash-plans/{cash_plan_id}/suggestions/accept",
    response_model=list[CashPlanItemResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Accept cash plan suggestions",
)
def accept_cash_plan_suggestions(
    organization_id: UUID,
    cash_plan_id: UUID,
    payload: AcceptCashPlanSuggestionsRequest,
    _membership: RequireWriter,
    command: Annotated[
        AcceptCashPlanSuggestionsCommand, Depends(get_accept_cash_plan_suggestions_command)
    ],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> list[CashPlanItemResponse]:
    try:
        with uow:
            created = command.execute(
                AcceptCashPlanSuggestionsInput(
                    organization_id=organization_id,
                    cash_plan_id=cash_plan_id,
                    suggestions=tuple(
                        AcceptSuggestionItem(
                            item_type=s.item_type,
                            description=s.description,
                            expected_date=s.expected_date,
                            amount=s.amount,
                            probability=s.probability,
                            linked_entity_type=s.linked_entity_type,
                            linked_entity_id=s.linked_entity_id,
                            notes=s.notes,
                        )
                        for s in payload.suggestions
                    ),
                )
            )
            uow.commit()
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return [CashPlanItemResponse.from_entity(item) for item in created]


@router.get(
    "/{organization_id}/cash-plans/{cash_plan_id}/projection",
    response_model=CashProjectionResponse,
    summary="Cash projection",
    description=(
        "Projects daily (or aggregated) balances under a scenario:\n"
        "- **committed**: only confirmed / 100% probability remaining amounts\n"
        "- **expected**: probability-weighted inflows; full outflows\n"
        "- **optimistic**: all remaining planned amounts\n\n"
        "`safe_to_spend` is included as a caveat-laden operational estimate."
    ),
)
def get_cash_projection(
    organization_id: UUID,
    cash_plan_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetCashProjectionQuery, Depends(get_cash_projection_query)],
    scenario: Annotated[
        Literal["committed", "expected", "optimistic"],
        Query(),
    ] = "expected",
    granularity: Annotated[
        Literal["day", "week", "month"],
        Query(),
    ] = "day",
) -> CashProjectionResponse:
    try:
        result = query.execute(
            organization_id,
            cash_plan_id,
            scenario=scenario,
            granularity=granularity,
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return CashProjectionResponse.from_result(result)


@router.get(
    "/{organization_id}/cash-plans/{cash_plan_id}/alerts",
    response_model=CashAlertListResponse,
    summary="Cash plan alerts",
)
def get_cash_plan_alerts(
    organization_id: UUID,
    cash_plan_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetCashPlanAlertsQuery, Depends(get_cash_plan_alerts_query)],
    scenario: Annotated[
        Literal["committed", "expected", "optimistic"],
        Query(),
    ] = "expected",
) -> CashAlertListResponse:
    try:
        alerts = query.execute(organization_id, cash_plan_id, scenario=scenario)
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    items = [CashAlertResponse.from_alert(a) for a in alerts]
    return CashAlertListResponse(items=items, total=len(items))
