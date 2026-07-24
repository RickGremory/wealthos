"""Domain tests for transaction value objects and entries."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.entities.transaction_entry import (
    TransactionEntry,
)
from wealthos.modules.transactions.domain.exceptions import (
    InvalidTransactionType,
    SameAccountTransfer,
    TransactionAlreadyVoided,
    TransactionDescriptionEmpty,
    ZeroEntryAmount,
)
from wealthos.modules.transactions.domain.value_objects.transaction_description import (
    TransactionDescription,
)
from wealthos.modules.transactions.domain.value_objects.transaction_type import (
    TransactionType,
)
from wealthos.shared.domain.value_objects.money import Money


def test_entry_rejects_zero_amount() -> None:
    with pytest.raises(ZeroEntryAmount):
        TransactionEntry.create(
            transaction_id=uuid4(),
            account_id=uuid4(),
            amount=Money("0.00", "MXN"),
        )


def test_entry_keeps_decimal_and_currency() -> None:
    entry = TransactionEntry.create(
        transaction_id=uuid4(),
        account_id=uuid4(),
        amount=Money("1250.50", "MXN"),
    )
    assert entry.amount.amount == Decimal("1250.50")
    assert entry.amount.currency.value == "MXN"


def test_transaction_type_and_description() -> None:
    assert TransactionType("income").is_income
    with pytest.raises(InvalidTransactionType):
        TransactionType("pending")
    with pytest.raises(TransactionDescriptionEmpty):
        TransactionDescription(" ")


def test_income_expense_transfer_and_void() -> None:
    org = uuid4()
    user = uuid4()
    account = uuid4()
    category = uuid4()
    from datetime import UTC, datetime

    income = Transaction.create_income(
        organization_id=org,
        account_id=account,
        category_id=category,
        amount=Money("100.00", "MXN"),
        description="Pago",
        occurred_at=datetime.now(UTC),
        created_by_user_id=user,
    )
    assert income.status.is_posted
    assert income.entries[0].amount.amount == Decimal("100.00")

    expense = Transaction.create_expense(
        organization_id=org,
        account_id=account,
        category_id=category,
        amount=Money("50.00", "MXN"),
        description="Gasto",
        occurred_at=datetime.now(UTC),
        created_by_user_id=user,
    )
    assert expense.entries[0].amount.amount == Decimal("-50.00")

    other = uuid4()
    transfer = Transaction.create_transfer(
        organization_id=org,
        source_account_id=account,
        destination_account_id=other,
        amount=Money("10.00", "MXN"),
        description="Move",
        occurred_at=datetime.now(UTC),
        created_by_user_id=user,
    )
    assert len(transfer.entries) == 2
    assert sum(e.amount.amount for e in transfer.entries) == Decimal("0.00")

    with pytest.raises(SameAccountTransfer):
        Transaction.create_transfer(
            organization_id=org,
            source_account_id=account,
            destination_account_id=account,
            amount=Money("10.00", "MXN"),
            description="Bad",
            occurred_at=datetime.now(UTC),
            created_by_user_id=user,
        )

    income.void(voided_by_user_id=user)
    assert income.status.is_voided
    with pytest.raises(TransactionAlreadyVoided):
        income.void(voided_by_user_id=user)
