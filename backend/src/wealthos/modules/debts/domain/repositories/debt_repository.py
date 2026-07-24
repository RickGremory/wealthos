"""Persistence port for Debt aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt import Debt


class DebtRepository(Protocol):
    def add(self, debt: Debt) -> Debt: ...

    def get_by_id(self, organization_id: UUID, debt_id: UUID) -> Debt | None: ...

    def get_active_by_account(
        self,
        organization_id: UUID,
        account_id: UUID,
    ) -> Debt | None: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        debt_type: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[Debt]: ...

    def save(self, debt: Debt) -> Debt: ...
