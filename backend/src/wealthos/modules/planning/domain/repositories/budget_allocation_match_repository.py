"""Persistence port for BudgetAllocationMatch records."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget_allocation_match import (
    BudgetAllocationMatch,
)


class BudgetAllocationMatchRepository(Protocol):
    def add(self, match: BudgetAllocationMatch) -> BudgetAllocationMatch: ...

    def list_by_allocation(
        self,
        organization_id: UUID,
        budget_allocation_id: UUID,
    ) -> list[BudgetAllocationMatch]: ...

    def list_by_budget(
        self,
        organization_id: UUID,
        budget_id: UUID,
    ) -> list[BudgetAllocationMatch]: ...

    def remove(self, match: BudgetAllocationMatch) -> None: ...
