"""Map CashPlanItemMatch ↔ CashPlanItemMatchModel."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.cash_plan_item_match import CashPlanItemMatch
from wealthos.modules.planning.infrastructure.models.planning_models import (
    CashPlanItemMatchModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class CashPlanItemMatchMapper(BaseMapper[CashPlanItemMatchModel, CashPlanItemMatch]):
    def to_entity(self, model: CashPlanItemMatchModel) -> CashPlanItemMatch:
        return CashPlanItemMatch(
            id=model.id,
            organization_id=model.organization_id,
            cash_plan_item_id=model.cash_plan_item_id,
            transaction_id=model.transaction_id,
            matched_amount=Money(model.matched_amount, model.currency),
            created_at=model.created_at,
        )

    def to_model(self, entity: CashPlanItemMatch) -> CashPlanItemMatchModel:
        return CashPlanItemMatchModel(
            id=entity.id,
            organization_id=entity.organization_id,
            cash_plan_item_id=entity.cash_plan_item_id,
            transaction_id=entity.transaction_id,
            matched_amount=entity.matched_amount.amount,
            currency=entity.matched_amount.currency.value,
            created_at=entity.created_at,
        )
