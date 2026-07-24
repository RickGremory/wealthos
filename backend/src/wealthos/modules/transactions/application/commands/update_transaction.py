"""Update transaction metadata command."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.exceptions import (
    CategoryInactive,
    CategoryNotAllowedForTransfer,
    CategoryNotFoundError,
    TransactionCategoryTypeMismatch,
    TransactionNotFoundError,
)
from wealthos.modules.transactions.domain.repositories.transaction_repository import (
    TransactionRepository,
)


@dataclass(frozen=True, slots=True)
class UpdateTransactionInput:
    organization_id: UUID
    transaction_id: UUID
    updated_by_user_id: UUID
    description: str | None = None
    notes: str | None = None
    occurred_at: datetime | None = None
    category_id: UUID | None = None
    fields_set: frozenset[str] = field(default_factory=frozenset)


class UpdateTransactionCommand:
    def __init__(
        self,
        repository: TransactionRepository,
        categories: CategoryRepository,
    ) -> None:
        self._repository = repository
        self._categories = categories

    def execute(self, data: UpdateTransactionInput) -> Transaction:
        transaction = self._repository.get_by_id(
            data.organization_id,
            data.transaction_id,
        )
        if transaction is None:
            raise TransactionNotFoundError("Transaction not found.")

        if "category_id" in data.fields_set:
            self._validate_category_change(transaction, data.category_id)

        transaction.update_metadata(
            updated_by_user_id=data.updated_by_user_id,
            description=data.description,
            notes=data.notes,
            occurred_at=data.occurred_at,
            category_id=data.category_id,
            fields_set=data.fields_set,
        )
        return self._repository.save(transaction)

    def _validate_category_change(
        self,
        transaction: Transaction,
        category_id: UUID | None,
    ) -> None:
        if transaction.transaction_type.is_transfer:
            if category_id is not None:
                raise CategoryNotAllowedForTransfer("Transfers cannot have a category.")
            return

        if category_id is None:
            if transaction.transaction_type.is_income or transaction.transaction_type.is_expense:
                raise CategoryNotFoundError("Category is required.")
            return

        category = self._categories.get_by_id(
            transaction.organization_id,
            category_id,
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
