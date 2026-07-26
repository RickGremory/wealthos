"""HTTP routes for Planning projection / Safe To Spend (SPEC-004)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.planning.api.dependencies import (
    get_cancel_planned_cash_flow_command,
    get_create_planned_cash_flow_command,
    get_get_planning_projection_query,
    get_get_planning_settings_query,
    get_get_planning_sources_query,
    get_get_safe_to_spend_summary_query,
    get_list_planned_cash_flows_query,
    get_simulate_planning_scenario_query,
    get_update_planned_cash_flow_command,
    get_update_planning_settings_command,
)
from wealthos.modules.planning.api.exception_mapping import http_map_planning_errors
from wealthos.modules.planning.application.commands.cancel_planned_cash_flow import (
    CancelPlannedCashFlowCommand,
    CancelPlannedCashFlowInput,
)
from wealthos.modules.planning.application.commands.create_planned_cash_flow import (
    CreatePlannedCashFlowCommand,
    CreatePlannedCashFlowInput,
)
from wealthos.modules.planning.application.commands.update_planned_cash_flow import (
    UpdatePlannedCashFlowCommand,
    UpdatePlannedCashFlowInput,
)
from wealthos.modules.planning.application.commands.update_planning_settings import (
    UpdatePlanningSettingsCommand,
    UpdatePlanningSettingsInput,
)
from wealthos.modules.planning.application.queries.get_planning_projection import (
    GetPlanningProjectionInput,
    GetPlanningProjectionQuery,
    GetSafeToSpendSummaryQuery,
)
from wealthos.modules.planning.application.queries.get_planning_settings import (
    GetPlanningSettingsInput,
    GetPlanningSettingsQuery,
)
from wealthos.modules.planning.application.queries.get_planning_sources import (
    GetPlanningSourcesInput,
    GetPlanningSourcesQuery,
)
from wealthos.modules.planning.application.queries.list_planned_cash_flows import (
    ListPlannedCashFlowsInput,
    ListPlannedCashFlowsQuery,
)
from wealthos.modules.planning.application.queries.simulate_planning_scenario import (
    ScenarioAdjustmentInput,
    SimulatePlanningScenarioInput,
    SimulatePlanningScenarioQuery,
)
from wealthos.modules.planning.domain.exceptions import PlanningError
from wealthos.modules.planning.schemas.planning_projection import (
    CreatePlannedCashFlowRequest,
    PlannedCashFlowResponse,
    PlanningProjectionResponse,
    PlanningSettingsResponse,
    PlanningSourceSummaryResponse,
    SafeToSpendSummaryResponse,
    ScenarioSimulationResponse,
    SimulatePlanningScenarioRequest,
    UpdatePlannedCashFlowRequest,
    UpdatePlanningSettingsRequest,
)

router = APIRouter(prefix="/{organization_id}/planning", tags=["planning-projection"])

RequireMember = OrganizationMember
RequireWriter = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]


@router.get("/projection", response_model=PlanningProjectionResponse)
def get_projection(
    organization_id: UUID,
    _membership: RequireMember,
    query: Annotated[GetPlanningProjectionQuery, Depends(get_get_planning_projection_query)],
    currency: Annotated[str, Query(min_length=3, max_length=3)],
    horizon: Annotated[
        str | None,
        Query(pattern="^(today|7_days|30_days|90_days)$"),
    ] = None,
) -> PlanningProjectionResponse:
    try:
        result = query.execute(
            GetPlanningProjectionInput(
                organization_id=organization_id,
                currency=currency.upper(),
                horizon=horizon,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return PlanningProjectionResponse.from_result(result)


@router.get("/safe-to-spend", response_model=SafeToSpendSummaryResponse)
def get_safe_to_spend(
    organization_id: UUID,
    _membership: RequireMember,
    query: Annotated[
        GetSafeToSpendSummaryQuery,
        Depends(get_get_safe_to_spend_summary_query),
    ],
    currency: Annotated[str, Query(min_length=3, max_length=3)],
    horizon: Annotated[
        str | None,
        Query(pattern="^(today|7_days|30_days|90_days)$"),
    ] = None,
) -> SafeToSpendSummaryResponse:
    try:
        summary = query.execute(
            GetPlanningProjectionInput(
                organization_id=organization_id,
                currency=currency.upper(),
                horizon=horizon,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return SafeToSpendSummaryResponse(
        organization_id=summary.organization_id,
        currency=summary.currency,
        horizon=summary.horizon.value,
        safe_to_spend=summary.safe_to_spend,
        status=summary.status,
        confidence=summary.confidence,
        reserve_shortfall=summary.reserve_shortfall,
        cash_deficit=summary.cash_deficit,
        lowest_balance_at=summary.lowest_balance_at,
        calculated_at=summary.calculated_at,
    )


@router.get("/sources", response_model=list[PlanningSourceSummaryResponse])
def get_sources(
    organization_id: UUID,
    _membership: RequireMember,
    query: Annotated[GetPlanningSourcesQuery, Depends(get_get_planning_sources_query)],
    currency: Annotated[str, Query(min_length=3, max_length=3)],
    horizon: Annotated[
        str | None,
        Query(pattern="^(today|7_days|30_days|90_days)$"),
    ] = None,
) -> list[PlanningSourceSummaryResponse]:
    try:
        sources = query.execute(
            GetPlanningSourcesInput(
                organization_id=organization_id,
                currency=currency.upper(),
                horizon=horizon,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return [PlanningSourceSummaryResponse.from_summary(source) for source in sources]


@router.get("/settings", response_model=PlanningSettingsResponse)
def get_settings(
    organization_id: UUID,
    _membership: RequireMember,
    query: Annotated[GetPlanningSettingsQuery, Depends(get_get_planning_settings_query)],
) -> PlanningSettingsResponse:
    settings = query.execute(GetPlanningSettingsInput(organization_id=organization_id))
    return PlanningSettingsResponse.from_entity(settings)


@router.put("/settings", response_model=PlanningSettingsResponse)
def put_settings(
    organization_id: UUID,
    body: UpdatePlanningSettingsRequest,
    _membership: RequireWriter,
    command: Annotated[
        UpdatePlanningSettingsCommand,
        Depends(get_update_planning_settings_command),
    ],
) -> PlanningSettingsResponse:
    try:
        settings = command.execute(
            UpdatePlanningSettingsInput(
                organization_id=organization_id,
                expected_version=body.version,
                default_horizon=body.default_horizon,
                safety_reserve_strategy=body.safety_reserve_strategy,
                safety_reserve_amount=body.safety_reserve_amount,
                linked_emergency_goal_id=body.linked_emergency_goal_id,
                include_expected_income=body.include_expected_income,
                include_estimated_expenses=body.include_estimated_expenses,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return PlanningSettingsResponse.from_entity(settings)


@router.get("/cash-flows", response_model=list[PlannedCashFlowResponse])
def list_cash_flows(
    organization_id: UUID,
    _membership: RequireMember,
    query: Annotated[ListPlannedCashFlowsQuery, Depends(get_list_planned_cash_flows_query)],
    currency: Annotated[str | None, Query(min_length=3, max_length=3)] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> list[PlannedCashFlowResponse]:
    items = query.execute(
        ListPlannedCashFlowsInput(
            organization_id=organization_id,
            currency=currency.upper() if currency else None,
            status=status_filter,
        )
    )
    return [PlannedCashFlowResponse.from_entity(item) for item in items]


@router.post(
    "/cash-flows",
    response_model=PlannedCashFlowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_cash_flow(
    organization_id: UUID,
    body: CreatePlannedCashFlowRequest,
    _membership: RequireWriter,
    command: Annotated[
        CreatePlannedCashFlowCommand,
        Depends(get_create_planned_cash_flow_command),
    ],
) -> PlannedCashFlowResponse:
    try:
        entity = command.execute(
            CreatePlannedCashFlowInput(
                organization_id=organization_id,
                name=body.name,
                direction=body.direction,
                amount=body.amount,
                currency=body.currency,
                expected_at=body.expected_at,
                certainty=body.certainty,
                notes=body.notes,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return PlannedCashFlowResponse.from_entity(entity)


@router.patch("/cash-flows/{cash_flow_id}", response_model=PlannedCashFlowResponse)
def update_cash_flow(
    organization_id: UUID,
    cash_flow_id: UUID,
    body: UpdatePlannedCashFlowRequest,
    _membership: RequireWriter,
    command: Annotated[
        UpdatePlannedCashFlowCommand,
        Depends(get_update_planned_cash_flow_command),
    ],
) -> PlannedCashFlowResponse:
    fields = frozenset(body.model_fields_set - {"version"})
    try:
        entity = command.execute(
            UpdatePlannedCashFlowInput(
                organization_id=organization_id,
                cash_flow_id=cash_flow_id,
                expected_version=body.version,
                name=body.name,
                direction=body.direction,
                amount=body.amount,
                expected_at=body.expected_at,
                certainty=body.certainty,
                notes=body.notes,
                fields_set=fields,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return PlannedCashFlowResponse.from_entity(entity)


@router.delete("/cash-flows/{cash_flow_id}", response_model=PlannedCashFlowResponse)
def cancel_cash_flow(
    organization_id: UUID,
    cash_flow_id: UUID,
    _membership: RequireWriter,
    command: Annotated[
        CancelPlannedCashFlowCommand,
        Depends(get_cancel_planned_cash_flow_command),
    ],
) -> PlannedCashFlowResponse:
    try:
        entity = command.execute(
            CancelPlannedCashFlowInput(
                organization_id=organization_id,
                cash_flow_id=cash_flow_id,
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return PlannedCashFlowResponse.from_entity(entity)


@router.post("/scenarios/simulate", response_model=ScenarioSimulationResponse)
def simulate_scenario(
    organization_id: UUID,
    body: SimulatePlanningScenarioRequest,
    _membership: RequireMember,
    query: Annotated[
        SimulatePlanningScenarioQuery,
        Depends(get_simulate_planning_scenario_query),
    ],
) -> ScenarioSimulationResponse:
    try:
        result = query.execute(
            SimulatePlanningScenarioInput(
                organization_id=organization_id,
                currency=body.currency,
                horizon=body.horizon,
                adjustments=tuple(
                    ScenarioAdjustmentInput(
                        kind=item.kind,
                        direction=item.direction,
                        amount=item.amount,
                        expected_at=item.expected_at,
                        label=item.label,
                        certainty=item.certainty,
                        adjustment_id=item.adjustment_id,
                    )
                    for item in body.adjustments
                ),
            )
        )
    except PlanningError as exc:
        raise http_map_planning_errors(exc) from exc
    return ScenarioSimulationResponse.from_result(result)
