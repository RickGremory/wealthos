"""Map Goal ↔ GoalModel."""

from __future__ import annotations

from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.domain.value_objects.goal_name import GoalName
from wealthos.modules.goals.domain.value_objects.goal_status import GoalStatus
from wealthos.modules.goals.domain.value_objects.goal_strategy import GoalStrategy
from wealthos.modules.goals.infrastructure.models.goal_model import (
    GoalAccountModel,
    GoalModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class GoalMapper(BaseMapper[GoalModel, Goal]):
    def to_entity(self, model: GoalModel) -> Goal:
        return Goal(
            id=model.id,
            organization_id=model.organization_id,
            name=GoalName(model.name),
            target_amount=Money(model.target_amount, model.currency),
            target_date=model.target_date,
            strategy=GoalStrategy(model.strategy),
            linked_account_ids=tuple(link.account_id for link in model.account_links),
            status=GoalStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: Goal) -> GoalModel:
        model = GoalModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name.value,
            target_amount=entity.target_amount.amount,
            currency=entity.target_amount.currency.value,
            target_date=entity.target_date,
            strategy=entity.strategy.value,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            completed_at=entity.completed_at,
            archived_at=entity.archived_at,
        )
        model.account_links = [
            GoalAccountModel(goal_id=entity.id, account_id=account_id)
            for account_id in entity.linked_account_ids
        ]
        return model

    def apply_to_model(self, entity: Goal, model: GoalModel) -> GoalModel:
        model.name = entity.name.value
        model.target_amount = entity.target_amount.amount
        model.currency = entity.target_amount.currency.value
        model.target_date = entity.target_date
        model.strategy = entity.strategy.value
        model.status = entity.status.value
        model.updated_at = entity.updated_at
        model.completed_at = entity.completed_at
        model.archived_at = entity.archived_at
        model.account_links.clear()
        for account_id in entity.linked_account_ids:
            model.account_links.append(GoalAccountModel(goal_id=entity.id, account_id=account_id))
        return model
