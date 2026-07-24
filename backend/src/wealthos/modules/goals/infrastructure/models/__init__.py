"""ORM models package for goals."""

from wealthos.modules.goals.infrastructure.models.goal_model import (
    GoalAccountModel,
    GoalManualProgressModel,
    GoalModel,
)

__all__ = ["GoalAccountModel", "GoalManualProgressModel", "GoalModel"]
