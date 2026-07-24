"""Persistence port for CashPlanItem records."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan_item import CashPlanItem


class CashPlanItemRepository(Protocol):
    def add(self, item: CashPlanItem) -> CashPlanItem: ...

    def get_by_id(
        self,
        organization_id: UUID,
        item_id: UUID,
    ) -> CashPlanItem | None: ...

    def list_by_plan(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
        *,
        include_cancelled: bool = True,
    ) -> list[CashPlanItem]: ...

    def save(self, item: CashPlanItem) -> CashPlanItem: ...

    def remove(self, item: CashPlanItem) -> None: ...

    def lock_for_update(
        self,
        organization_id: UUID,
        item_id: UUID,
    ) -> CashPlanItem | None: ...
