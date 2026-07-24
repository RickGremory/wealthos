"""Atomic posting of transaction entries onto account balances."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import (
    AccountInactive,
    AccountNotFoundError,
    CategoryInactive,
    CategoryNotAllowedForTransfer,
    CategoryNotFoundError,
    CrossCurrencyTransferNotSupported,
    EntryCurrencyMismatch,
    TransactionCategoryTypeMismatch,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)
from wealthos.shared.domain.value_objects.money import Money


class TransactionPostingService:
    """Persist a transaction and apply entry deltas under account row locks."""

    def __init__(
        self,
        *,
        transactions: TransactionRepository,
        accounts: AccountRepository,
        categories: CategoryRepository,
    ) -> None:
        self._transactions = transactions
        self._accounts = accounts
        self._categories = categories

    def post(self, transaction: Transaction) -> Transaction:
        self._validate_category(transaction)
        accounts = self._lock_accounts(transaction)
        self._validate_accounts_for_post(transaction, accounts)
        stored = self._transactions.add(transaction)
        self._apply_deltas(accounts, stored, reverse=False)
        return stored

    def void(self, transaction: Transaction, *, voided_by_user_id: UUID) -> Transaction:
        accounts = self._lock_accounts(transaction)
        transaction.void(voided_by_user_id=voided_by_user_id)
        stored = self._transactions.save(transaction)
        self._apply_deltas(accounts, stored, reverse=True)
        return stored

    def _lock_accounts(self, transaction: Transaction) -> dict[UUID, Account]:
        account_ids = [entry.account_id for entry in transaction.entries]
        locked = self._accounts.get_many_for_update(
            transaction.organization_id,
            account_ids,
        )
        by_id = {account.id: account for account in locked}
        for account_id in account_ids:
            if account_id not in by_id:
                raise AccountNotFoundError("Account not found.")
        return by_id

    def _validate_accounts_for_post(
        self,
        transaction: Transaction,
        accounts: dict[UUID, Account],
    ) -> None:
        if transaction.transaction_type.is_transfer and len(transaction.entries) == 2:
            source = accounts[transaction.entries[0].account_id]
            destination = accounts[transaction.entries[1].account_id]
            if source.currency != destination.currency:
                raise CrossCurrencyTransferNotSupported(
                    "Transfers between different currencies are not supported."
                )

        for entry in transaction.entries:
            account = accounts[entry.account_id]
            if not account.is_active:
                raise AccountInactive("Cannot post to an archived account.")
            if entry.amount.currency != account.currency:
                raise EntryCurrencyMismatch("Entry currency must match the account currency.")

    def _validate_category(self, transaction: Transaction) -> None:
        if transaction.transaction_type.is_transfer:
            if transaction.category_id is not None:
                raise CategoryNotAllowedForTransfer("Transfers cannot have a category.")
            return

        if transaction.category_id is None:
            if transaction.transaction_type.is_income or transaction.transaction_type.is_expense:
                raise CategoryNotFoundError("Category is required.")
            return

        category = self._categories.get_by_id(
            transaction.organization_id,
            transaction.category_id,
        )
        if category is None:
            raise CategoryNotFoundError("Category not found.")
        if not category.is_active:
            raise CategoryInactive("Category is inactive.")

        if transaction.transaction_type.is_income and not category.category_type.is_income:
            raise TransactionCategoryTypeMismatch("Income transactions require an income category.")
        if transaction.transaction_type.is_expense and not category.category_type.is_expense:
            raise TransactionCategoryTypeMismatch(
                "Expense transactions require an expense category."
            )

    def _apply_deltas(
        self,
        accounts: dict[UUID, Account],
        transaction: Transaction,
        *,
        reverse: bool,
    ) -> None:
        for entry in transaction.entries:
            account = accounts[entry.account_id]
            delta = entry.amount
            if reverse:
                delta = Money(-delta.amount, delta.currency)
            account.apply_balance_delta(delta)
            self._accounts.save(account)
