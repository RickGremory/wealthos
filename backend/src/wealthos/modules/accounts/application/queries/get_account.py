"""GetAccount query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.exceptions import AccountNotFoundError
from wealthos.modules.accounts.domain.repositories.account_repository import AccountRepository


class GetAccountQuery:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def execute(self, organization_id: UUID, account_id: UUID) -> Account:
        account = self._repository.get_by_id(organization_id, account_id)
        if account is None:
            raise AccountNotFoundError("Account not found.")
        return account
