"""Persistence port for CashPlan aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan


class CashPlanRepository(Protocol):
    def add(self, cash_plan: CashPlan) -> CashPlan: ...

    def get_by_id(self, organization_id: UUID, cash_plan_id: UUID) -> CashPlan | None: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[CashPlan]: ...

    def save(self, cash_plan: CashPlan) -> CashPlan: ...

    def list_account_ids(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
    ) -> list[UUID]: ...

    def replace_account_ids(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
        account_ids: list[UUID],
    ) -> None: ...
