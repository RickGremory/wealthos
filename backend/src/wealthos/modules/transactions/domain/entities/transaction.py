"""Transaction aggregate — posted financial movement with ledger entries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.transactions.domain.entities.transaction_entry import (
    TransactionEntry,
)
from wealthos.modules.transactions.domain.exceptions import (
    CategoryNotAllowedForTransfer,
    InvalidTransactionEntries,
    SameAccountTransfer,
    TransactionAlreadyVoided,
)
from wealthos.modules.transactions.domain.value_objects.transaction_description import (
    TransactionDescription,
)
from wealthos.modules.transactions.domain.value_objects.transaction_status import (
    TransactionStatus,
)
from wealthos.modules.transactions.domain.value_objects.transaction_type import (
    TransactionType,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class Transaction:
    id: UUID
    organization_id: UUID
    transaction_type: TransactionType
    description: TransactionDescription
    category_id: UUID | None
    occurred_at: datetime
    notes: str | None
    status: TransactionStatus
    entries: list[TransactionEntry]
    created_by_user_id: UUID
    updated_by_user_id: UUID
    voided_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime
    voided_at: datetime | None

    @classmethod
    def create_income(
        cls,
        *,
        organization_id: UUID,
        account_id: UUID,
        category_id: UUID,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        notes: str | None = None,
        transaction_id: UUID | None = None,
    ) -> Transaction:
        if amount.amount <= Decimal("0.00"):
            raise InvalidTransactionEntries("Income amount must be positive.")
        return cls._create_single_entry(
            organization_id=organization_id,
            transaction_type="income",
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            description=description,
            occurred_at=occurred_at,
            created_by_user_id=created_by_user_id,
            notes=notes,
            transaction_id=transaction_id,
        )

    @classmethod
    def create_expense(
        cls,
        *,
        organization_id: UUID,
        account_id: UUID,
        category_id: UUID,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        notes: str | None = None,
        transaction_id: UUID | None = None,
    ) -> Transaction:
        """`amount` is the positive magnitude from the API; stored as negative."""
        if amount.amount <= Decimal("0.00"):
            raise InvalidTransactionEntries("Expense amount must be positive.")
        signed = Money(-amount.amount, amount.currency)
        return cls._create_single_entry(
            organization_id=organization_id,
            transaction_type="expense",
            account_id=account_id,
            category_id=category_id,
            amount=signed,
            description=description,
            occurred_at=occurred_at,
            created_by_user_id=created_by_user_id,
            notes=notes,
            transaction_id=transaction_id,
        )

    @classmethod
    def create_adjustment(
        cls,
        *,
        organization_id: UUID,
        account_id: UUID,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        category_id: UUID | None = None,
        notes: str | None = None,
        transaction_id: UUID | None = None,
    ) -> Transaction:
        if amount.amount == Decimal("0.00"):
            raise InvalidTransactionEntries("Adjustment amount cannot be zero.")
        return cls._create_single_entry(
            organization_id=organization_id,
            transaction_type="adjustment",
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            description=description,
            occurred_at=occurred_at,
            created_by_user_id=created_by_user_id,
            notes=notes,
            transaction_id=transaction_id,
        )

    @classmethod
    def create_transfer(
        cls,
        *,
        organization_id: UUID,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        notes: str | None = None,
        transaction_id: UUID | None = None,
    ) -> Transaction:
        if source_account_id == destination_account_id:
            raise SameAccountTransfer("Transfer accounts must be different.")
        if amount.amount <= Decimal("0.00"):
            raise InvalidTransactionEntries("Transfer amount must be positive.")

        now = datetime.now(UTC)
        tx_id = transaction_id or uuid4()
        debit = TransactionEntry.create(
            transaction_id=tx_id,
            account_id=source_account_id,
            amount=Money(-amount.amount, amount.currency),
        )
        credit = TransactionEntry.create(
            transaction_id=tx_id,
            account_id=destination_account_id,
            amount=Money(amount.amount, amount.currency),
        )
        if debit.amount.amount + credit.amount.amount != Decimal("0.00"):
            raise InvalidTransactionEntries("Transfer entries must sum to zero.")

        return cls(
            id=tx_id,
            organization_id=organization_id,
            transaction_type=TransactionType("transfer"),
            description=TransactionDescription(description),
            category_id=None,
            occurred_at=occurred_at,
            notes=_clean_notes(notes),
            status=TransactionStatus("posted"),
            entries=[debit, credit],
            created_by_user_id=created_by_user_id,
            updated_by_user_id=created_by_user_id,
            voided_by_user_id=None,
            created_at=now,
            updated_at=now,
            voided_at=None,
        )

    @classmethod
    def _create_single_entry(
        cls,
        *,
        organization_id: UUID,
        transaction_type: str,
        account_id: UUID,
        category_id: UUID | None,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        notes: str | None,
        transaction_id: UUID | None,
    ) -> Transaction:
        now = datetime.now(UTC)
        tx_id = transaction_id or uuid4()
        entry = TransactionEntry.create(
            transaction_id=tx_id,
            account_id=account_id,
            amount=amount,
        )
        return cls(
            id=tx_id,
            organization_id=organization_id,
            transaction_type=TransactionType(transaction_type),
            description=TransactionDescription(description),
            category_id=category_id,
            occurred_at=occurred_at,
            notes=_clean_notes(notes),
            status=TransactionStatus("posted"),
            entries=[entry],
            created_by_user_id=created_by_user_id,
            updated_by_user_id=created_by_user_id,
            voided_by_user_id=None,
            created_at=now,
            updated_at=now,
            voided_at=None,
        )

    def update_metadata(
        self,
        *,
        updated_by_user_id: UUID,
        description: str | None = None,
        notes: str | None = None,
        occurred_at: datetime | None = None,
        category_id: UUID | None = None,
        fields_set: frozenset[str] | None = None,
    ) -> None:
        fields = fields_set or frozenset()
        if self.status.is_voided:
            raise TransactionAlreadyVoided("Cannot update a voided transaction.")
        if self.transaction_type.is_transfer and "category_id" in fields:
            if category_id is not None:
                raise CategoryNotAllowedForTransfer("Transfers cannot have a category.")
        if "description" in fields and description is not None:
            self.description = TransactionDescription(description)
        if "notes" in fields:
            self.notes = _clean_notes(notes)
        if "occurred_at" in fields and occurred_at is not None:
            self.occurred_at = occurred_at
        if "category_id" in fields:
            self.category_id = category_id
        self.updated_by_user_id = updated_by_user_id
        self.updated_at = datetime.now(UTC)

    def void(self, *, voided_by_user_id: UUID) -> None:
        if self.status.is_voided or self.voided_at is not None:
            raise TransactionAlreadyVoided("Transaction is already voided.")
        now = datetime.now(UTC)
        self.status = TransactionStatus("voided")
        self.voided_at = now
        self.voided_by_user_id = voided_by_user_id
        self.updated_by_user_id = voided_by_user_id
        self.updated_at = now


def _clean_notes(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
