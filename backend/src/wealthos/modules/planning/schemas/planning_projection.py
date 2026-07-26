"""Pydantic schemas for the Planning projection spine (SPEC-004)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from wealthos.modules.planning.domain.entities.planned_cash_flow import PlannedCashFlow
from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.services.scenario_engine import ScenarioSimulationResult
from wealthos.modules.planning.domain.value_objects.alerts import PlanningSourceSummary
from wealthos.modules.planning.domain.value_objects.projection_result import (
    PlanningProjectionResult,
)


def _money(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"{value:.2f}"


class CreatePlannedCashFlowRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    direction: Literal["inflow", "outflow"]
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    expected_at: datetime
    certainty: Literal["confirmed", "expected", "estimated"] = "expected"
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("name")
    @classmethod
    def trim_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("notes")
    @classmethod
    def empty_notes_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class UpdatePlannedCashFlowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    direction: Literal["inflow", "outflow"] | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    expected_at: datetime | None = None
    certainty: Literal["confirmed", "expected", "estimated"] | None = None
    notes: str | None = Field(default=None, max_length=500)


class PlannedCashFlowResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    direction: str
    amount: str
    currency: str
    expected_at: datetime
    certainty: str
    status: str
    notes: str | None
    settled_transaction_id: UUID | None
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: PlannedCashFlow) -> PlannedCashFlowResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name,
            direction=entity.direction.value,
            amount=_money(entity.amount.amount) or "0.00",
            currency=entity.amount.currency.value,
            expected_at=entity.expected_at,
            certainty=entity.certainty.value,
            status=entity.status.value,
            notes=entity.notes,
            settled_transaction_id=entity.settled_transaction_id,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class UpdatePlanningSettingsRequest(BaseModel):
    version: int | None = Field(default=None, ge=1)
    default_horizon: Literal["today", "7_days", "30_days", "90_days"]
    safety_reserve_strategy: Literal[
        "none",
        "fixed_amount",
        "linked_goal",
        "percentage_of_cash",
        "days_of_expenses",
    ]
    safety_reserve_amount: Decimal | None = Field(default=None, ge=0)
    linked_emergency_goal_id: UUID | None = None
    include_expected_income: bool = True
    include_estimated_expenses: bool = True

    @model_validator(mode="after")
    def validate_reserve_configuration(self) -> UpdatePlanningSettingsRequest:
        if self.safety_reserve_strategy == "fixed_amount" and self.safety_reserve_amount is None:
            raise ValueError("safety_reserve_amount is required for fixed_amount")
        if (
            self.safety_reserve_strategy == "linked_goal"
            and self.linked_emergency_goal_id is None
        ):
            raise ValueError("linked_emergency_goal_id is required for linked_goal")
        return self


class PlanningSettingsResponse(BaseModel):
    id: UUID
    organization_id: UUID
    default_horizon: str
    safety_reserve_strategy: str
    safety_reserve_amount: str | None
    linked_emergency_goal_id: UUID | None
    include_expected_income: bool
    include_estimated_expenses: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: PlanningSettings) -> PlanningSettingsResponse:
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
            default_horizon=entity.default_horizon.value,
            safety_reserve_strategy=entity.safety_reserve_strategy.value,
            safety_reserve_amount=_money(entity.safety_reserve_amount),
            linked_emergency_goal_id=entity.linked_emergency_goal_id,
            include_expected_income=entity.include_expected_income,
            include_estimated_expenses=entity.include_estimated_expenses,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class PlanningAlertResponse(BaseModel):
    code: str
    severity: str
    message_key: str
    related_resource_type: str | None = None
    related_resource_id: str | None = None
    date: datetime | None = None
    amount: str | None = None
    currency: str | None = None


class PlanningBreakdownItemResponse(BaseModel):
    id: str
    category: str
    label: str
    amount: str
    currency: str
    date: datetime | None
    direction: str
    source_name: str
    source_id: str | None
    certainty: str | None
    included: bool
    exclusion_reason: str | None = None


class PlanningProjectionPointResponse(BaseModel):
    occurred_at: datetime
    balance_before: str | None = None
    amount: str
    balance_after: str
    cash_flow_id: str | None = None
    occurrence_key: str | None = None
    label: str
    category: str
    direction: str | None = None
    certainty: str | None = None
    source_name: str | None = None


class PlanningExplanationResponse(BaseModel):
    steps: list[dict[str, Any]]
    required_reserve: str
    minimum_balance: str | None
    minimum_balance_at: datetime | None
    safe_to_spend: str | None
    binding_constraint: str


class PlanningProjectionResponse(BaseModel):
    organization_id: UUID
    currency: str
    horizon: str
    period_start: datetime
    period_end: datetime
    calculated_at: datetime
    status: str
    confidence: str
    confidence_reasons: list[str]
    current_available_cash: str
    expected_income: str
    committed_outflows: str
    protected_funds: str
    safe_to_spend: str | None
    projected_ending_balance: str | None
    minimum_projected_balance: str | None
    lowest_balance_at: datetime | None
    cash_deficit: str | None
    reserve_shortfall: str | None
    timeline: list[PlanningProjectionPointResponse]
    breakdown: list[PlanningBreakdownItemResponse]
    alerts: list[PlanningAlertResponse]
    explanations: PlanningExplanationResponse
    sources: list[dict[str, Any]]

    @classmethod
    def from_result(cls, result: PlanningProjectionResult) -> PlanningProjectionResponse:
        return cls(
            organization_id=result.organization_id,
            currency=result.currency,
            horizon=result.horizon.value,
            period_start=result.period.start,
            period_end=result.period.end,
            calculated_at=result.calculated_at,
            status=result.status.value,
            confidence=result.confidence.value,
            confidence_reasons=list(result.confidence_reasons),
            current_available_cash=_money(result.current_available_cash) or "0.00",
            expected_income=_money(result.expected_income) or "0.00",
            committed_outflows=_money(result.committed_outflows) or "0.00",
            protected_funds=_money(result.reserved_funds) or "0.00",
            safe_to_spend=_money(result.safe_to_spend),
            projected_ending_balance=_money(result.projected_ending_balance),
            minimum_projected_balance=_money(result.minimum_projected_balance),
            lowest_balance_at=result.minimum_balance_at,
            cash_deficit=_money(result.cash_deficit),
            reserve_shortfall=_money(result.reserve_shortfall),
            timeline=[
                PlanningProjectionPointResponse(
                    occurred_at=point.at,
                    amount=_money(point.delta) or "0.00",
                    balance_after=_money(point.balance) or "0.00",
                    cash_flow_id=point.flow_id,
                    occurrence_key=point.occurrence_key,
                    label=point.label,
                    category=point.category,
                    direction=point.direction.value if point.direction else None,
                    certainty=point.certainty.value if point.certainty else None,
                    source_name=point.source_name,
                )
                for point in result.timeline
            ],
            breakdown=[
                PlanningBreakdownItemResponse(
                    id=item.id,
                    category=item.category,
                    label=item.label,
                    amount=_money(item.amount) or "0.00",
                    currency=item.currency,
                    date=item.date,
                    direction=item.direction,
                    source_name=item.source_name,
                    source_id=item.source_id,
                    certainty=item.certainty.value if item.certainty else None,
                    included=item.included,
                    exclusion_reason=item.exclusion_reason,
                )
                for item in result.breakdown
            ],
            alerts=[
                PlanningAlertResponse(
                    code=alert.code,
                    severity=alert.severity.value,
                    message_key=alert.message_key,
                    related_resource_type=alert.related_resource_type,
                    related_resource_id=alert.related_resource_id,
                    date=alert.date,
                    amount=_money(alert.amount),
                    currency=alert.currency,
                )
                for alert in result.alerts
            ],
            explanations=PlanningExplanationResponse(
                steps=[
                    {
                        "key": step.key,
                        "label": step.label,
                        "amount": _money(step.amount),
                        "running_balance": _money(step.running_balance),
                    }
                    for step in result.explanation.steps
                ],
                required_reserve=_money(result.explanation.required_reserve) or "0.00",
                minimum_balance=_money(result.explanation.minimum_balance),
                minimum_balance_at=result.explanation.minimum_balance_at,
                safe_to_spend=_money(result.explanation.safe_to_spend),
                binding_constraint=result.explanation.binding_constraint,
            ),
            sources=[
                {
                    "source_name": source.source_name,
                    "status": source.status.value,
                    "collected_at": source.collected_at.isoformat(),
                    "data_as_of": source.data_as_of.isoformat() if source.data_as_of else None,
                    "accounts": source.accounts,
                    "cash_flows": source.cash_flows,
                    "reservations": source.reservations,
                    "settlements": source.settlements,
                }
                for source in result.sources
            ],
        )


class SafeToSpendSummaryResponse(BaseModel):
    organization_id: UUID
    currency: str
    horizon: str
    safe_to_spend: str | None
    status: str
    confidence: str
    reserve_shortfall: str
    cash_deficit: str
    lowest_balance_at: str | None
    calculated_at: str


class PlanningSourceSummaryResponse(BaseModel):
    source_name: str
    status: str
    collected_at: datetime
    data_as_of: datetime | None
    accounts: int
    cash_flows: int
    reservations: int
    settlements: int

    @classmethod
    def from_summary(cls, source: PlanningSourceSummary) -> PlanningSourceSummaryResponse:
        return cls(
            source_name=source.source_name,
            status=source.status.value,
            collected_at=source.collected_at,
            data_as_of=source.data_as_of,
            accounts=source.accounts,
            cash_flows=source.cash_flows,
            reservations=source.reservations,
            settlements=source.settlements,
        )


class AddCashFlowAdjustmentSchema(BaseModel):
    kind: Literal["add_cash_flow"] = "add_cash_flow"
    direction: Literal["inflow", "outflow"]
    amount: Decimal = Field(gt=0)
    expected_at: datetime
    label: str = Field(min_length=1, max_length=120)
    certainty: Literal["confirmed", "expected", "estimated"] = "expected"
    adjustment_id: str | None = None


class SimulatePlanningScenarioRequest(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    horizon: Literal["today", "7_days", "30_days", "90_days"] | None = None
    adjustments: Annotated[list[AddCashFlowAdjustmentSchema], Field(min_length=1, max_length=20)]

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.strip().upper()


class ScenarioSimulationResponse(BaseModel):
    baseline: PlanningProjectionResponse
    scenario: PlanningProjectionResponse
    impact: dict[str, Any]

    @classmethod
    def from_result(cls, result: ScenarioSimulationResult) -> ScenarioSimulationResponse:
        impact = result.impact
        return cls(
            baseline=PlanningProjectionResponse.from_result(result.baseline),
            scenario=PlanningProjectionResponse.from_result(result.scenario),
            impact={
                "safe_to_spend_before": _money(impact.safe_to_spend_before),
                "safe_to_spend_after": _money(impact.safe_to_spend_after),
                "safe_to_spend_delta": _money(impact.safe_to_spend_delta),
                "minimum_balance_before": _money(impact.minimum_balance_before),
                "minimum_balance_after": _money(impact.minimum_balance_after),
                "minimum_balance_delta": _money(impact.minimum_balance_delta),
                "status_before": impact.status_before.value,
                "status_after": impact.status_after.value,
                "status_changed": impact.status_changed,
            },
        )
