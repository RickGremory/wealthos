"""Goal response schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.goals.application.queries.get_goal import GoalWithProgress
from wealthos.modules.goals.application.queries.get_goals_dashboard_summary import (
    GoalsDashboardSummary,
)


class GoalResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    target_amount: Decimal
    currency: str
    target_date: date | None
    strategy: str
    linked_account_ids: list[UUID]
    status: str
    current_amount: Decimal
    remaining_amount: Decimal
    completion_percentage: Decimal
    estimated_completion_date: date | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    archived_at: datetime | None

    @classmethod
    def from_goal_with_progress(cls, item: GoalWithProgress) -> GoalResponse:
        goal = item.goal
        progress = item.progress
        return cls(
            id=goal.id,
            organization_id=goal.organization_id,
            name=goal.name.value,
            target_amount=goal.target_amount.amount,
            currency=goal.target_amount.currency.value,
            target_date=goal.target_date,
            strategy=goal.strategy.value,
            linked_account_ids=list(goal.linked_account_ids),
            status=goal.status.value,
            current_amount=progress.current_amount.amount,
            remaining_amount=progress.remaining_amount.amount,
            completion_percentage=progress.completion_percentage,
            estimated_completion_date=progress.estimated_completion_date,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            completed_at=goal.completed_at,
            archived_at=goal.archived_at,
        )


class GoalListResponse(BaseModel):
    items: list[GoalResponse]
    total: int


class GoalsDashboardResponse(BaseModel):
    active_goals: int
    completed_goals: int
    total_target: Decimal
    current_progress: Decimal
    completion: Decimal
    top_goals: list[GoalResponse]

    @classmethod
    def from_summary(cls, summary: GoalsDashboardSummary) -> GoalsDashboardResponse:
        return cls(
            active_goals=summary.active_goals,
            completed_goals=summary.completed_goals,
            total_target=summary.total_target,
            current_progress=summary.current_progress,
            completion=summary.completion,
            top_goals=[
                GoalResponse.from_goal_with_progress(item) for item in summary.top_goals
            ],
        )
