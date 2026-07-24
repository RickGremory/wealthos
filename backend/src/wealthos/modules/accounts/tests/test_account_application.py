"""Account application tests with in-memory repository."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from wealthos.modules.accounts.application.commands.archive_account import (
    ArchiveAccountCommand,
    ArchiveAccountInput,
)
from wealthos.modules.accounts.application.commands.create_account import (
    CreateAccountCommand,
    CreateAccountInput,
)
from wealthos.modules.accounts.application.commands.update_account import (
    UpdateAccountCommand,
    UpdateAccountInput,
)
from wealthos.modules.accounts.application.queries.get_account import GetAccountQuery
from wealthos.modules.accounts.application.queries.list_accounts import ListAccountsQuery
from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.exceptions import AccountNotFoundError


class InMemoryAccountRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], Account] = {}

    def add(self, account: Account) -> Account:
        self._items[(account.organization_id, account.id)] = account
        return account

    def get_by_id(self, organization_id: UUID, account_id: UUID) -> Account | None:
        return self._items.get((organization_id, account_id))

    def get_many_for_update(
        self,
        organization_id: UUID,
        account_ids: list[UUID],
    ) -> list[Account]:
        return [
            self._items[(organization_id, account_id)]
            for account_id in sorted(set(account_ids))
            if (organization_id, account_id) in self._items
        ]

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[Account]:
        accounts = [a for (org_id, _), a in self._items.items() if org_id == organization_id]
        if not include_archived:
            accounts = [a for a in accounts if a.is_active]
        return sorted(accounts, key=lambda a: (not a.is_active, a.name.value))

    def save(self, account: Account) -> Account:
        self._items[(account.organization_id, account.id)] = account
        return account


def test_create_list_get_update_archive_flow() -> None:
    repo = InMemoryAccountRepository()
    org_id = uuid4()
    other_org = uuid4()

    created = CreateAccountCommand(repo).execute(
        CreateAccountInput(
            organization_id=org_id,
            name="HSBC Nómina",
            account_type="checking",
            currency="MXN",
            opening_balance=Decimal("1000.00"),
            institution_name="HSBC",
            last_four="1234",
        )
    )
    CreateAccountCommand(repo).execute(
        CreateAccountInput(
            organization_id=other_org,
            name="Other",
            account_type="cash",
            currency="MXN",
        )
    )

    listed = ListAccountsQuery(repo).execute(org_id)
    assert len(listed) == 1
    assert listed[0].id == created.id

    fetched = GetAccountQuery(repo).execute(org_id, created.id)
    assert fetched.name.value == "HSBC Nómina"

    with pytest.raises(AccountNotFoundError):
        GetAccountQuery(repo).execute(other_org, created.id)

    updated = UpdateAccountCommand(repo).execute(
        UpdateAccountInput(
            organization_id=org_id,
            account_id=created.id,
            name="HSBC Payroll",
            fields_set=frozenset({"name"}),
        )
    )
    assert updated.name.value == "HSBC Payroll"

    archived = ArchiveAccountCommand(repo).execute(
        ArchiveAccountInput(organization_id=org_id, account_id=created.id)
    )
    assert archived.is_active is False
    assert ListAccountsQuery(repo).execute(org_id) == []
    assert len(ListAccountsQuery(repo).execute(org_id, include_archived=True)) == 1
