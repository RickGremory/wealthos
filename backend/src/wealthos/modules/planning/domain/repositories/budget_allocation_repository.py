"""Persistence port for BudgetAllocation records."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget_allocation import BudgetAllocation


class BudgetAllocationRepository(Protocol):
    def add(self, allocation: BudgetAllocation) -> BudgetAllocation: ...

    def get_by_id(
        self,
        organization_id: UUID,
        allocation_id: UUID,
    ) -> BudgetAllocation | None: ...

    def list_by_budget(
        self,
        organization_id: UUID,
        budget_id: UUID,
    ) -> list[BudgetAllocation]: ...

    def save(self, allocation: BudgetAllocation) -> BudgetAllocation: ...

    def remove(self, allocation: BudgetAllocation) -> None: ...
