"""Map Budget ↔ BudgetModel."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.budget import Budget
from wealthos.modules.planning.domain.value_objects.budget_name import BudgetName
from wealthos.modules.planning.domain.value_objects.budget_period_type import BudgetPeriodType
from wealthos.modules.planning.domain.value_objects.budget_status import BudgetStatus
from wealthos.modules.planning.domain.value_objects.forecast_method import ForecastMethod
from wealthos.modules.planning.domain.value_objects.rollover_policy import RolloverPolicy
from wealthos.modules.planning.infrastructure.models.planning_models import BudgetModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.currency import Currency


class BudgetMapper(BaseMapper[BudgetModel, Budget]):
    def to_entity(self, model: BudgetModel) -> Budget:
        return Budget(
            id=model.id,
            organization_id=model.organization_id,
            name=BudgetName(model.name),
            period_type=BudgetPeriodType(model.period_type),
            date_from=model.date_from,
            date_to=model.date_to,
            currency=Currency(model.currency),
            status=BudgetStatus(model.status),
            rollover_policy=RolloverPolicy(model.rollover_policy),
            forecast_method=ForecastMethod(model.forecast_method),
            created_at=model.created_at,
            updated_at=model.updated_at,
            closed_at=model.closed_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: Budget) -> BudgetModel:
        return BudgetModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name.value,
            period_type=entity.period_type.value,
            date_from=entity.date_from,
            date_to=entity.date_to,
            currency=entity.currency.value,
            status=entity.status.value,
            rollover_policy=entity.rollover_policy.value,
            forecast_method=entity.forecast_method.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            closed_at=entity.closed_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: Budget, model: BudgetModel) -> BudgetModel:
        model.name = entity.name.value
        model.period_type = entity.period_type.value
        model.date_from = entity.date_from
        model.date_to = entity.date_to
        model.currency = entity.currency.value
        model.status = entity.status.value
        model.rollover_policy = entity.rollover_policy.value
        model.forecast_method = entity.forecast_method.value
        model.updated_at = entity.updated_at
        model.closed_at = entity.closed_at
        model.archived_at = entity.archived_at
        return model
