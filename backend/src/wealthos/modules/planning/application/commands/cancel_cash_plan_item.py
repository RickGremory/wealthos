"""CancelCashPlanItem command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.exceptions import (
    CashPlanItemNotFoundError,
    CashPlanNotFoundError,
)
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)


@dataclass(frozen=True, slots=True)
class CancelCashPlanItemInput:
    organization_id: UUID
    cash_plan_id: UUID
    item_id: UUID


class CancelCashPlanItemCommand:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items

    def execute(self, data: CancelCashPlanItemInput) -> CashPlanItem:
        plan = self._cash_plans.get_by_id(data.organization_id, data.cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        plan.ensure_editable()

        item = self._items.get_by_id(data.organization_id, data.item_id)
        if item is None or item.cash_plan_id != data.cash_plan_id:
            raise CashPlanItemNotFoundError("Cash plan item not found.")
        item.cancel()
        return self._items.save(item)
