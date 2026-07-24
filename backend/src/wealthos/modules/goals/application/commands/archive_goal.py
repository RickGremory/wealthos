"""ArchiveGoal command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.exceptions import GoalNotFoundError
from wealthos.modules.goals.domain.repositories.goal_repository import GoalRepository


@dataclass(frozen=True, slots=True)
class ArchiveGoalInput:
    organization_id: UUID
    goal_id: UUID


class ArchiveGoalCommand:
    def __init__(self, goals: GoalRepository) -> None:
        self._goals = goals

    def execute(self, data: ArchiveGoalInput) -> Goal:
        goal = self._goals.get_by_id(data.organization_id, data.goal_id)
        if goal is None:
            raise GoalNotFoundError("Goal not found.")
        goal.archive()
        return self._goals.save(goal)
