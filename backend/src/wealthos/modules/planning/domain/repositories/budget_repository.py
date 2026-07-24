"""Persistence port for Budget aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.planning.domain.entities.budget import Budget


class BudgetRepository(Protocol):
    def add(self, budget: Budget) -> Budget: ...

    def get_by_id(self, organization_id: UUID, budget_id: UUID) -> Budget | None: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[Budget]: ...

    def save(self, budget: Budget) -> Budget: ...
