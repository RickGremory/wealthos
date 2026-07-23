"""Account domain tests."""

from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.exceptions import (
    AccountAlreadyArchived,
    InvalidAccountType,
)
from wealthos.modules.accounts.domain.value_objects.account_type import AccountType


def test_account_type_assets_and_liabilities() -> None:
    assert AccountType("checking").is_asset is True
    assert AccountType("credit_card").is_liability is True
    assert AccountType("loan").classification == "liability"


def test_account_type_rejects_invalid() -> None:
    with pytest.raises(InvalidAccountType):
        AccountType("crypto")


def test_account_create_sets_balances_and_active() -> None:
    account = Account.create(
        organization_id=uuid4(),
        name="HSBC Nómina",
        account_type="checking",
        currency="MXN",
        opening_balance=Decimal("15000.00"),
    )
    assert account.is_active is True
    assert account.archived_at is None
    assert account.current_balance.amount == Decimal("15000.00")
    assert account.opening_balance.amount == Decimal("15000.00")


def test_account_rename_and_archive() -> None:
    account = Account.create(
        organization_id=uuid4(),
        name="HSBC",
        account_type="checking",
        currency="MXN",
    )
    account.rename("HSBC Nómina")
    assert account.name.value == "HSBC Nómina"
    account.archive()
    assert account.is_active is False
    assert account.archived_at is not None
    with pytest.raises(AccountAlreadyArchived):
        account.archive()
