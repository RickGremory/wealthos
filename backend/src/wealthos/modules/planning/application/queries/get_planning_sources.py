"""List planning source diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.application.queries.get_planning_projection import (
    GetPlanningProjectionInput,
    GetPlanningProjectionQuery,
)
from wealthos.modules.planning.domain.value_objects.alerts import PlanningSourceSummary


@dataclass(frozen=True, slots=True)
class GetPlanningSourcesInput:
    organization_id: UUID
    currency: str
    horizon: str | None = None


class GetPlanningSourcesQuery:
    def __init__(self, projection: GetPlanningProjectionQuery) -> None:
        self._projection = projection

    def execute(self, data: GetPlanningSourcesInput) -> tuple[PlanningSourceSummary, ...]:
        context = self._projection.build_context(
            GetPlanningProjectionInput(
                organization_id=data.organization_id,
                currency=data.currency,
                horizon=data.horizon,
            )
        )
        return context.sources
