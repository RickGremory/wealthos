"""Persistence port for CashPlanItemMatch records."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan_item_match import CashPlanItemMatch


class CashPlanItemMatchRepository(Protocol):
    def add(self, match: CashPlanItemMatch) -> CashPlanItemMatch: ...

    def list_by_item(
        self,
        organization_id: UUID,
        cash_plan_item_id: UUID,
    ) -> list[CashPlanItemMatch]: ...

    def list_by_plan(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
    ) -> list[CashPlanItemMatch]: ...

    def sum_matched_amount(
        self,
        organization_id: UUID,
        cash_plan_item_id: UUID,
    ) -> Decimal: ...

    def remove(self, match: CashPlanItemMatch) -> None: ...
