"""UpdateAccount command."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.exceptions import AccountNotFoundError
from wealthos.modules.accounts.domain.repositories.account_repository import AccountRepository


@dataclass(frozen=True, slots=True)
class UpdateAccountInput:
    organization_id: UUID
    account_id: UUID
    name: str | None = None
    institution_name: str | None = None
    last_four: str | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateAccountCommand:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def execute(self, data: UpdateAccountInput) -> Account:
        account = self._repository.get_by_id(data.organization_id, data.account_id)
        if account is None:
            raise AccountNotFoundError("Account not found.")

        if "name" in data.fields_set and data.name is not None:
            account.rename(data.name)
        if "institution_name" in data.fields_set:
            account.change_institution(data.institution_name)
        if "last_four" in data.fields_set:
            account.change_last_four(data.last_four)

        return self._repository.save(account)
