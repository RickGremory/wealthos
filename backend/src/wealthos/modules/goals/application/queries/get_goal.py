"""GetGoal / ListGoals queries with derived progress."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from wealthos.modules.goals.application.services.goal_progress_service import (
    GoalProgressService,
)
from wealthos.modules.goals.application.views.goal_progress import GoalProgress
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.exceptions import GoalNotFoundError
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository


@dataclass(frozen=True, slots=True)
class GoalWithProgress:
    goal: Goal
    progress: GoalProgress


class GetGoalQuery:
    def __init__(
        self,
        goals: GoalRepository,
        progress_service: GoalProgressService,
    ) -> None:
        self._goals = goals
        self._progress = progress_service

    def execute(self, organization_id: UUID, goal_id: UUID) -> GoalWithProgress:
        goal = self._goals.get_by_id(organization_id, goal_id)
        if goal is None:
            raise GoalNotFoundError("Goal not found.")
        goal = self._maybe_complete(goal)
        return GoalWithProgress(goal=goal, progress=self._progress.calculate(goal))

    def _maybe_complete(self, goal: Goal) -> Goal:
        progress = self._progress.calculate(goal)
        if progress.completion_percentage >= Decimal("100") and goal.status.is_active:
            goal.complete()
            return self._goals.save(goal)
        return goal


class ListGoalsQuery:
    def __init__(
        self,
        goals: GoalRepository,
        progress_service: GoalProgressService,
    ) -> None:
        self._goals = goals
        self._progress = progress_service

    def execute(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[GoalWithProgress]:
        items: list[GoalWithProgress] = []
        for goal in self._goals.list_by_organization(
            organization_id,
            include_archived=include_archived,
        ):
            progress = self._progress.calculate(goal)
            if progress.completion_percentage >= Decimal("100") and goal.status.is_active:
                goal.complete()
                goal = self._goals.save(goal)
                progress = self._progress.calculate(goal)
            items.append(GoalWithProgress(goal=goal, progress=progress))
        # Closest to completion first (highest percentage).
        items.sort(
            key=lambda item: item.progress.completion_percentage,
            reverse=True,
        )
        return items
