"""Persistence port for Account aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account


class AccountRepository(Protocol):
    """Domain-facing account repository (always scoped by organization)."""

    def add(self, account: Account) -> Account: ...

    def get_by_id(self, organization_id: UUID, account_id: UUID) -> Account | None: ...

    def get_many_for_update(
        self,
        organization_id: UUID,
        account_ids: list[UUID],
    ) -> list[Account]: ...

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[Account]: ...

    def save(self, account: Account) -> Account: ...
