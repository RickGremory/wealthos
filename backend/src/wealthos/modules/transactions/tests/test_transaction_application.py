"""Transaction application tests with in-memory repositories."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType
from wealthos.modules.transactions.application.commands.create_expense import (
    CreateExpenseCommand,
    CreateExpenseInput,
)
from wealthos.modules.transactions.application.commands.create_income import (
    CreateIncomeCommand,
    CreateIncomeInput,
)
from wealthos.modules.transactions.application.commands.create_transfer import (
    CreateTransferCommand,
    CreateTransferInput,
)
from wealthos.modules.transactions.application.commands.void_transaction import (
    VoidTransactionCommand,
    VoidTransactionInput,
)
from wealthos.modules.transactions.application.services.transaction_posting_service import (
    TransactionPostingService,
)
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import (
    AccountInactive,
    AccountNotFoundError,
    CategoryNotFoundError,
    CrossCurrencyTransferNotSupported,
    TransactionCategoryTypeMismatch,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionFilters,
    TransactionListResult,
)


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
        accounts = [a for (org, _), a in self._items.items() if org == organization_id]
        if not include_archived:
            accounts = [a for a in accounts if a.is_active]
        return accounts

    def save(self, account: Account) -> Account:
        self._items[(account.organization_id, account.id)] = account
        return account


class InMemoryCategoryRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], Category] = {}

    def add(self, category: Category) -> Category:
        self._items[(category.organization_id, category.id)] = category
        return category

    def add_many(self, categories: list[Category]) -> list[Category]:
        for category in categories:
            self.add(category)
        return categories

    def get_by_id(self, organization_id: UUID, category_id: UUID) -> Category | None:
        return self._items.get((organization_id, category_id))

    def exists_by_normalized_name(self, *args, **kwargs) -> bool:  # noqa: ANN002
        return False

    def list_by_organization(self, *args, **kwargs) -> list[Category]:  # noqa: ANN002
        return []

    def count_active_children(self, *args, **kwargs) -> int:  # noqa: ANN002
        return 0

    def save(self, category: Category) -> Category:
        self._items[(category.organization_id, category.id)] = category
        return category


class InMemoryTransactionRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], Transaction] = {}

    def add(self, transaction: Transaction) -> Transaction:
        self._items[(transaction.organization_id, transaction.id)] = transaction
        return transaction

    def get_by_id(
        self,
        organization_id: UUID,
        transaction_id: UUID,
    ) -> Transaction | None:
        return self._items.get((organization_id, transaction_id))

    def list_by_organization(
        self,
        organization_id: UUID,
        filters: TransactionFilters,
    ) -> TransactionListResult:
        items = [t for (org, _), t in self._items.items() if org == organization_id]
        return TransactionListResult(items=items, total=len(items))

    def save(self, transaction: Transaction) -> Transaction:
        self._items[(transaction.organization_id, transaction.id)] = transaction
        return transaction


def _setup() -> tuple[
    InMemoryAccountRepository,
    InMemoryCategoryRepository,
    InMemoryTransactionRepository,
    TransactionPostingService,
    UUID,
    UUID,
    Account,
    Category,
    Category,
]:
    accounts = InMemoryAccountRepository()
    categories = InMemoryCategoryRepository()
    transactions = InMemoryTransactionRepository()
    posting = TransactionPostingService(
        transactions=transactions,
        accounts=accounts,
        categories=categories,
    )
    org = uuid4()
    user = uuid4()
    account = Account.create(
        organization_id=org,
        name="HSBC",
        account_type="checking",
        currency="MXN",
        opening_balance=Decimal("20000.00"),
    )
    accounts.add(account)
    income_cat = Category.create(
        organization_id=org,
        name="Honorarios",
        category_type="income",
    )
    expense_cat = Category.create(
        organization_id=org,
        name="Alimentación",
        category_type="expense",
    )
    categories.add(income_cat)
    categories.add(expense_cat)
    return (
        accounts,
        categories,
        transactions,
        posting,
        org,
        user,
        account,
        income_cat,
        expense_cat,
    )


def test_income_expense_transfer_void_balances() -> None:
    accounts, _, transactions, posting, org, user, hsbc, income_cat, expense_cat = _setup()
    gbm = Account.create(
        organization_id=org,
        name="GBM",
        account_type="investment",
        currency="MXN",
        opening_balance=Decimal("0.00"),
    )
    accounts.add(gbm)
    now = datetime.now(UTC)

    CreateIncomeCommand(posting, accounts).execute(
        CreateIncomeInput(
            organization_id=org,
            account_id=hsbc.id,
            category_id=income_cat.id,
            amount=Decimal("10000.00"),
            description="Pago cliente",
            occurred_at=now,
            created_by_user_id=user,
        )
    )
    assert accounts.get_by_id(org, hsbc.id).current_balance.amount == Decimal("30000.00")

    expense = CreateExpenseCommand(posting, accounts).execute(
        CreateExpenseInput(
            organization_id=org,
            account_id=hsbc.id,
            category_id=expense_cat.id,
            amount=Decimal("1500.00"),
            description="Supermercado",
            occurred_at=now,
            created_by_user_id=user,
        )
    )
    assert accounts.get_by_id(org, hsbc.id).current_balance.amount == Decimal("28500.00")

    CreateTransferCommand(posting, accounts).execute(
        CreateTransferInput(
            organization_id=org,
            source_account_id=hsbc.id,
            destination_account_id=gbm.id,
            amount=Decimal("5000.00"),
            description="A GBM",
            occurred_at=now,
            created_by_user_id=user,
        )
    )
    assert accounts.get_by_id(org, hsbc.id).current_balance.amount == Decimal("23500.00")
    assert accounts.get_by_id(org, gbm.id).current_balance.amount == Decimal("5000.00")

    VoidTransactionCommand(transactions, posting).execute(
        VoidTransactionInput(
            organization_id=org,
            transaction_id=expense.id,
            voided_by_user_id=user,
        )
    )
    assert accounts.get_by_id(org, hsbc.id).current_balance.amount == Decimal("25000.00")


def test_rejects_inactive_account_wrong_category_and_cross_currency() -> None:
    accounts, categories, _, posting, org, user, hsbc, income_cat, expense_cat = _setup()
    now = datetime.now(UTC)
    hsbc.archive()
    accounts.save(hsbc)

    with pytest.raises(AccountInactive):
        CreateIncomeCommand(posting, accounts).execute(
            CreateIncomeInput(
                organization_id=org,
                account_id=hsbc.id,
                category_id=income_cat.id,
                amount=Decimal("10.00"),
                description="Fail",
                occurred_at=now,
                created_by_user_id=user,
            )
        )

    active = Account.create(
        organization_id=org,
        name="Cash",
        account_type="cash",
        currency="MXN",
    )
    accounts.add(active)
    with pytest.raises(TransactionCategoryTypeMismatch):
        CreateExpenseCommand(posting, accounts).execute(
            CreateExpenseInput(
                organization_id=org,
                account_id=active.id,
                category_id=income_cat.id,
                amount=Decimal("10.00"),
                description="Bad cat",
                occurred_at=now,
                created_by_user_id=user,
            )
        )

    with pytest.raises(CategoryNotFoundError):
        CreateIncomeCommand(posting, accounts).execute(
            CreateIncomeInput(
                organization_id=org,
                account_id=active.id,
                category_id=uuid4(),
                amount=Decimal("10.00"),
                description="Missing cat",
                occurred_at=now,
                created_by_user_id=user,
            )
        )

    usd = Account.create(
        organization_id=org,
        name="USD Wallet",
        account_type="cash",
        currency="USD",
    )
    accounts.add(usd)
    with pytest.raises(CrossCurrencyTransferNotSupported):
        CreateTransferCommand(posting, accounts).execute(
            CreateTransferInput(
                organization_id=org,
                source_account_id=active.id,
                destination_account_id=usd.id,
                amount=Decimal("10.00"),
                description="FX",
                occurred_at=now,
                created_by_user_id=user,
            )
        )

    with pytest.raises(AccountNotFoundError):
        CreateIncomeCommand(posting, accounts).execute(
            CreateIncomeInput(
                organization_id=org,
                account_id=uuid4(),
                category_id=income_cat.id,
                amount=Decimal("10.00"),
                description="Missing account",
                occurred_at=now,
                created_by_user_id=user,
            )
        )

    other_org_cat = Category.create(
        organization_id=uuid4(),
        name="Alien",
        category_type="income",
    )
    categories.add(other_org_cat)
    with pytest.raises(CategoryNotFoundError):
        CreateIncomeCommand(posting, accounts).execute(
            CreateIncomeInput(
                organization_id=org,
                account_id=active.id,
                category_id=other_org_cat.id,
                amount=Decimal("10.00"),
                description="Other org cat",
                occurred_at=now,
                created_by_user_id=user,
            )
        )

    assert CategoryType("income").is_income
