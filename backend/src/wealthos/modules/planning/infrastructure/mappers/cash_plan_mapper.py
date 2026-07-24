"""Map CashPlan ↔ CashPlanModel (account_ids live in cash_plan_accounts)."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.domain.value_objects.cash_buffer_type import CashBufferType
from wealthos.modules.planning.domain.value_objects.cash_plan_name import CashPlanName
from wealthos.modules.planning.domain.value_objects.cash_plan_status import CashPlanStatus
from wealthos.modules.planning.domain.value_objects.opening_balance_mode import (
    OpeningBalanceMode,
)
from wealthos.modules.planning.infrastructure.models.planning_models import CashPlanModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.currency import Currency
from wealthos.shared.domain.value_objects.money import Money


class CashPlanMapper(BaseMapper[CashPlanModel, CashPlan]):
    def to_entity(self, model: CashPlanModel) -> CashPlan:
        manual = None
        if model.manual_opening_balance is not None:
            manual = Money(model.manual_opening_balance, model.currency)
        return CashPlan(
            id=model.id,
            organization_id=model.organization_id,
            name=CashPlanName(model.name),
            date_from=model.date_from,
            date_to=model.date_to,
            currency=Currency(model.currency),
            opening_balance_mode=OpeningBalanceMode(model.opening_balance_mode),
            manual_opening_balance=manual,
            minimum_cash_buffer_type=CashBufferType(model.minimum_cash_buffer_type),
            minimum_cash_buffer_value=model.minimum_cash_buffer_value,
            status=CashPlanStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: CashPlan) -> CashPlanModel:
        return CashPlanModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name.value,
            date_from=entity.date_from,
            date_to=entity.date_to,
            currency=entity.currency.value,
            opening_balance_mode=entity.opening_balance_mode.value,
            manual_opening_balance=(
                entity.manual_opening_balance.amount
                if entity.manual_opening_balance is not None
                else None
            ),
            minimum_cash_buffer_type=entity.minimum_cash_buffer_type.value,
            minimum_cash_buffer_value=entity.minimum_cash_buffer_value,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: CashPlan, model: CashPlanModel) -> CashPlanModel:
        model.name = entity.name.value
        model.date_from = entity.date_from
        model.date_to = entity.date_to
        model.currency = entity.currency.value
        model.opening_balance_mode = entity.opening_balance_mode.value
        model.manual_opening_balance = (
            entity.manual_opening_balance.amount
            if entity.manual_opening_balance is not None
            else None
        )
        model.minimum_cash_buffer_type = entity.minimum_cash_buffer_type.value
        model.minimum_cash_buffer_value = entity.minimum_cash_buffer_value
        model.status = entity.status.value
        model.updated_at = entity.updated_at
        model.archived_at = entity.archived_at
        return model
