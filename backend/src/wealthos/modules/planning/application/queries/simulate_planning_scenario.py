"""Simulate a what-if scenario without persisting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.planning.application.queries.get_planning_projection import (
    GetPlanningProjectionInput,
    GetPlanningProjectionQuery,
)
from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
)
from wealthos.modules.planning.domain.services.scenario_engine import (
    AddCashFlowAdjustment,
    PlanningScenarioEngine,
    ScenarioSimulationResult,
)


@dataclass(frozen=True, slots=True)
class ScenarioAdjustmentInput:
    kind: str
    direction: str
    amount: Decimal
    expected_at: datetime
    label: str
    certainty: str = "expected"
    adjustment_id: str | None = None


@dataclass(frozen=True, slots=True)
class SimulatePlanningScenarioInput:
    organization_id: UUID
    currency: str
    horizon: str | None
    adjustments: tuple[ScenarioAdjustmentInput, ...]


class SimulatePlanningScenarioQuery:
    def __init__(
        self,
        projection: GetPlanningProjectionQuery,
        scenario_engine: PlanningScenarioEngine | None = None,
    ) -> None:
        self._projection = projection
        self._scenarios = scenario_engine or PlanningScenarioEngine()

    def execute(self, data: SimulatePlanningScenarioInput) -> ScenarioSimulationResult:
        context = self._projection.build_context(
            GetPlanningProjectionInput(
                organization_id=data.organization_id,
                currency=data.currency,
                horizon=data.horizon,
            )
        )
        adjustments = tuple(
            AddCashFlowAdjustment(
                adjustment_id=item.adjustment_id or str(uuid4()),
                direction=CashFlowDirection.parse(item.direction),
                amount=item.amount,
                expected_at=item.expected_at,
                label=item.label,
                certainty=CashFlowCertainty.parse(item.certainty),
            )
            for item in data.adjustments
            if item.kind == "add_cash_flow"
        )
        return self._scenarios.simulate(context, adjustments)
