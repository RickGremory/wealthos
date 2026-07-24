"""Dashboard goals summary projections."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.goals.application.queries.get_goal import (
    GoalWithProgress,
    ListGoalsQuery,
)
from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository


@dataclass(frozen=True, slots=True)
class GoalsDashboardSummary:
    active_goals: int
    completed_goals: int
    total_target: Decimal
    current_progress: Decimal
    completion: Decimal
    top_goals: tuple[GoalWithProgress, ...]


class GetGoalsDashboardSummaryQuery:
    def __init__(
        self,
        goals: GoalRepository,
        progress_service: GoalProgressService,
    ) -> None:
        self._list = ListGoalsQuery(goals, progress_service)

    def execute(
        self,
        organization_id: UUID,
        *,
        currency: str,
        top_limit: int = 5,
    ) -> GoalsDashboardSummary:
        items = self._list.execute(organization_id, include_archived=False)
        active = [item for item in items if item.goal.status.is_active]
        completed = [item for item in items if item.goal.status.is_completed]

        scoped = [
            item
            for item in items
            if item.goal.target_amount.currency.value == currency
            and not item.goal.status.is_archived
        ]
        total_target = sum(
            (item.goal.target_amount.amount for item in scoped),
            Decimal("0.00"),
        )
        current_progress = sum(
            (item.progress.current_amount.amount for item in scoped),
            Decimal("0.00"),
        )
        completion = (
            Decimal("0.00")
            if total_target <= 0
            else min(
                (current_progress * Decimal("100") / total_target).quantize(
                    Decimal("0.01")
                ),
                Decimal("100.00"),
            )
        )
        return GoalsDashboardSummary(
            active_goals=len(active),
            completed_goals=len(completed),
            total_target=total_target,
            current_progress=current_progress,
            completion=completion,
            top_goals=tuple(active[:top_limit]),
        )
