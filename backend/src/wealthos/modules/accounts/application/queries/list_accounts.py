"""ListAccounts query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.repositories.account_repository import AccountRepository


class ListAccountsQuery:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def execute(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[Account]:
        return self._repository.list_by_organization(
            organization_id,
            include_archived=include_archived,
        )
