"""Update manual progress for manual goals."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.application.views.goal_progress import GoalProgress
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.exceptions import (
    GoalNotFoundError,
    InvalidTargetAmount,
    StrategyDoesNotSupportManualProgress,
)
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository


@dataclass(frozen=True, slots=True)
class UpdateManualProgressInput:
    organization_id: UUID
    goal_id: UUID
    current_amount: Decimal


@dataclass(frozen=True, slots=True)
class UpdateManualProgressResult:
    goal: Goal
    progress: GoalProgress


class UpdateManualProgressCommand:
    def __init__(
        self,
        goals: GoalRepository,
        progress_service: GoalProgressService,
    ) -> None:
        self._goals = goals
        self._progress = progress_service

    def execute(self, data: UpdateManualProgressInput) -> UpdateManualProgressResult:
        goal = self._goals.get_by_id(data.organization_id, data.goal_id)
        if goal is None:
            raise GoalNotFoundError("Goal not found.")
        if not goal.strategy.is_manual:
            raise StrategyDoesNotSupportManualProgress(
                "Manual progress is only supported for manual goals."
            )
        if data.current_amount < 0:
            raise InvalidTargetAmount("Manual progress cannot be negative.")

        self._goals.set_manual_progress(goal.id, data.current_amount)
        progress = self._progress.calculate(goal)
        if (
            progress.completion_percentage >= Decimal("100")
            and goal.status.is_active
        ):
            goal.complete()
            goal = self._goals.save(goal)
            progress = self._progress.calculate(goal)
        return UpdateManualProgressResult(goal=goal, progress=progress)
