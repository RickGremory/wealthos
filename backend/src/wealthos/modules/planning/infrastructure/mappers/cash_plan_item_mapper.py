"""Map CashPlanItem ↔ CashPlanItemModel."""

from __future__ import annotations

from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.value_objects.cash_plan_item_status import (
    CashPlanItemStatus,
)
from wealthos.modules.planning.domain.value_objects.cash_plan_item_type import (
    CashPlanItemType,
)
from wealthos.modules.planning.domain.value_objects.linked_entity_type import (
    LinkedEntityType,
)
from wealthos.modules.planning.domain.value_objects.percentage import Percentage
from wealthos.modules.planning.infrastructure.models.planning_models import (
    CashPlanItemModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class CashPlanItemMapper(BaseMapper[CashPlanItemModel, CashPlanItem]):
    def to_entity(self, model: CashPlanItemModel) -> CashPlanItem:
        linked_type = (
            LinkedEntityType(model.linked_entity_type)
            if model.linked_entity_type is not None
            else None
        )
        return CashPlanItem(
            id=model.id,
            organization_id=model.organization_id,
            cash_plan_id=model.cash_plan_id,
            item_type=CashPlanItemType(model.item_type),
            description=model.description,
            expected_date=model.expected_date,
            amount=Money(model.amount, model.currency),
            probability=Percentage(model.probability),
            status=CashPlanItemStatus(model.status),
            category_id=model.category_id,
            account_id=model.account_id,
            linked_entity_type=linked_type,
            linked_entity_id=model.linked_entity_id,
            recurrence_rule=model.recurrence_rule,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            cancelled_at=model.cancelled_at,
        )

    def to_model(self, entity: CashPlanItem) -> CashPlanItemModel:
        return CashPlanItemModel(
            id=entity.id,
            organization_id=entity.organization_id,
            cash_plan_id=entity.cash_plan_id,
            item_type=entity.item_type.value,
            description=entity.description,
            expected_date=entity.expected_date,
            amount=entity.amount.amount,
            currency=entity.amount.currency.value,
            probability=entity.probability.value,
            status=entity.status.value,
            category_id=entity.category_id,
            account_id=entity.account_id,
            linked_entity_type=(
                entity.linked_entity_type.value if entity.linked_entity_type else None
            ),
            linked_entity_id=entity.linked_entity_id,
            recurrence_rule=entity.recurrence_rule,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            cancelled_at=entity.cancelled_at,
        )

    def apply_to_model(
        self,
        entity: CashPlanItem,
        model: CashPlanItemModel,
    ) -> CashPlanItemModel:
        model.item_type = entity.item_type.value
        model.description = entity.description
        model.expected_date = entity.expected_date
        model.amount = entity.amount.amount
        model.currency = entity.amount.currency.value
        model.probability = entity.probability.value
        model.status = entity.status.value
        model.category_id = entity.category_id
        model.account_id = entity.account_id
        model.linked_entity_type = (
            entity.linked_entity_type.value if entity.linked_entity_type else None
        )
        model.linked_entity_id = entity.linked_entity_id
        model.recurrence_rule = entity.recurrence_rule
        model.notes = entity.notes
        model.updated_at = entity.updated_at
        model.cancelled_at = entity.cancelled_at
        return model
