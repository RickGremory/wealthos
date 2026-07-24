"""GetCashPlan query."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem
from wealthos.modules.planning.domain.exceptions import CashPlanNotFoundError
from wealthos.modules.planning.domain.repositories.cash_plan_item_repository import (
    CashPlanItemRepository,
)
from wealthos.modules.planning.domain.repositories.cash_plan_repository import (
    CashPlanRepository,
)


@dataclass(frozen=True, slots=True)
class CashPlanDetail:
    cash_plan: CashPlan
    items: tuple[CashPlanItem, ...]
    account_ids: tuple[UUID, ...]


class GetCashPlanQuery:
    def __init__(
        self,
        cash_plans: CashPlanRepository,
        items: CashPlanItemRepository,
    ) -> None:
        self._cash_plans = cash_plans
        self._items = items

    def execute(self, organization_id: UUID, cash_plan_id: UUID) -> CashPlanDetail:
        plan = self._cash_plans.get_by_id(organization_id, cash_plan_id)
        if plan is None:
            raise CashPlanNotFoundError("Cash plan not found.")
        items = self._items.list_by_plan(organization_id, cash_plan_id)
        account_ids = self._cash_plans.list_account_ids(organization_id, cash_plan_id)
        return CashPlanDetail(
            cash_plan=plan,
            items=tuple(items),
            account_ids=tuple(account_ids),
        )
