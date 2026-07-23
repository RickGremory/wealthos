"""ArchiveAccount command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.exceptions import AccountNotFoundError
from wealthos.modules.accounts.domain.repositories.account_repository import AccountRepository


@dataclass(frozen=True, slots=True)
class ArchiveAccountInput:
    organization_id: UUID
    account_id: UUID


class ArchiveAccountCommand:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def execute(self, data: ArchiveAccountInput) -> Account:
        account = self._repository.get_by_id(data.organization_id, data.account_id)
        if account is None:
            raise AccountNotFoundError("Account not found.")
        account.archive()
        return self._repository.save(account)
