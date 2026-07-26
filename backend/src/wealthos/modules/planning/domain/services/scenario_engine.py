"""“¿Qué pasa si…?” — reuse the engine, mutate nothing (SPEC-004 §7)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.domain.enums.projection import ProjectionStatus
from wealthos.modules.planning.domain.enums.scenario import scenario_occurrence_key
from wealthos.modules.planning.domain.services.projection_engine import (
    PlanningProjectionEngine,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO, quantize_money
from wealthos.modules.planning.domain.value_objects.projection_result import (
    PlanningContext,
    PlanningProjectionResult,
)
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)

SCENARIO_SOURCE_NAME = "scenario"


@dataclass(frozen=True, slots=True)
class AddCashFlowAdjustment:
    """A hypothetical movement that exists only for this request."""

    adjustment_id: str
    direction: CashFlowDirection
    amount: Decimal
    expected_at: datetime
    label: str
    certainty: CashFlowCertainty = CashFlowCertainty.EXPECTED
    category: str = "scenario"

    def to_cash_flow(self, organization_id: UUID, currency: str) -> PlanningCashFlow:
        amount = quantize_money(self.amount)
        key = scenario_occurrence_key(self.adjustment_id)
        return PlanningCashFlow(
            id=key,
            organization_id=organization_id,
            direction=self.direction,
            amount=amount,
            outstanding_amount=amount,
            currency=currency,
            expected_at=self.expected_at,
            certainty=self.certainty,
            status=CashFlowStatus.ACTIVE,
            category=self.category,
            label=self.label,
            source=PlanningSourceReference(
                source_name=SCENARIO_SOURCE_NAME,
                resource_type="scenario_adjustment",
                resource_id=self.adjustment_id,
                occurrence_key=key,
            ),
        )


@dataclass(frozen=True, slots=True)
class ScenarioImpact:
    safe_to_spend_before: Decimal | None
    safe_to_spend_after: Decimal | None
    safe_to_spend_delta: Decimal | None
    minimum_balance_before: Decimal | None
    minimum_balance_after: Decimal | None
    minimum_balance_delta: Decimal | None
    status_before: ProjectionStatus
    status_after: ProjectionStatus
    status_changed: bool


@dataclass(frozen=True, slots=True)
class ScenarioSimulationResult:
    baseline: PlanningProjectionResult
    scenario: PlanningProjectionResult
    impact: ScenarioImpact


class PlanningScenarioEngine:
    """Simulations never touch ``planned_cash_flows``."""

    def __init__(self, engine: PlanningProjectionEngine | None = None) -> None:
        self._engine = engine or PlanningProjectionEngine()

    def simulate(
        self,
        context: PlanningContext,
        adjustments: tuple[AddCashFlowAdjustment, ...],
    ) -> ScenarioSimulationResult:
        baseline = self._engine.calculate(context)
        scenario_context = self.apply(context, adjustments)
        scenario = self._engine.calculate(scenario_context)
        return ScenarioSimulationResult(
            baseline=baseline,
            scenario=scenario,
            impact=calculate_impact(baseline, scenario),
        )

    def apply(
        self,
        context: PlanningContext,
        adjustments: tuple[AddCashFlowAdjustment, ...],
    ) -> PlanningContext:
        extra = tuple(
            adjustment.to_cash_flow(context.organization_id, context.currency)
            for adjustment in adjustments
        )
        return replace(context, cash_flows=(*context.cash_flows, *extra))


def calculate_impact(
    baseline: PlanningProjectionResult,
    scenario: PlanningProjectionResult,
) -> ScenarioImpact:
    return ScenarioImpact(
        safe_to_spend_before=baseline.safe_to_spend,
        safe_to_spend_after=scenario.safe_to_spend,
        safe_to_spend_delta=_delta(baseline.safe_to_spend, scenario.safe_to_spend),
        minimum_balance_before=baseline.minimum_projected_balance,
        minimum_balance_after=scenario.minimum_projected_balance,
        minimum_balance_delta=_delta(
            baseline.minimum_projected_balance,
            scenario.minimum_projected_balance,
        ),
        status_before=baseline.status,
        status_after=scenario.status,
        status_changed=baseline.status is not scenario.status,
    )


def _delta(before: Decimal | None, after: Decimal | None) -> Decimal | None:
    if before is None or after is None:
        return None
    return quantize_money(after - before) if after != before else ZERO
