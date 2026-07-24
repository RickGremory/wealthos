"""Map Transaction ↔ TransactionModel (with entries)."""

from __future__ import annotations

from wealthos.modules.transactions.domain.entities.transaction import Transaction
from wealthos.modules.transactions.domain.entities.transaction_entry import (
    TransactionEntry,
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
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class TransactionMapper(BaseMapper[TransactionModel, Transaction]):
    def to_entity(self, model: TransactionModel) -> Transaction:
        entries = [
            TransactionEntry(
                id=entry.id,
                transaction_id=entry.transaction_id,
                account_id=entry.account_id,
                amount=Money(entry.amount, entry.currency),
                created_at=entry.created_at,
            )
            for entry in model.entries
        ]
        return Transaction(
            id=model.id,
            organization_id=model.organization_id,
            transaction_type=TransactionType(model.transaction_type),
            description=TransactionDescription(model.description),
            category_id=model.category_id,
            occurred_at=model.occurred_at,
            notes=model.notes,
            status=TransactionStatus(model.status),
            entries=entries,
            created_by_user_id=model.created_by_user_id,
            updated_by_user_id=model.updated_by_user_id,
            voided_by_user_id=model.voided_by_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            voided_at=model.voided_at,
        )

    def to_model(self, entity: Transaction) -> TransactionModel:
        model = TransactionModel(
            id=entity.id,
            organization_id=entity.organization_id,
            transaction_type=entity.transaction_type.value,
            description=entity.description.value,
            category_id=entity.category_id,
            occurred_at=entity.occurred_at,
            notes=entity.notes,
            status=entity.status.value,
            created_by_user_id=entity.created_by_user_id,
            updated_by_user_id=entity.updated_by_user_id,
            voided_by_user_id=entity.voided_by_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            voided_at=entity.voided_at,
        )
        model.entries = [
            TransactionEntryModel(
                id=entry.id,
                transaction_id=entity.id,
                account_id=entry.account_id,
                amount=entry.amount.amount,
                currency=entry.amount.currency.value,
                created_at=entry.created_at,
            )
            for entry in entity.entries
        ]
        return model

    def apply_to_model(self, entity: Transaction, model: TransactionModel) -> TransactionModel:
        model.description = entity.description.value
        model.category_id = entity.category_id
        model.occurred_at = entity.occurred_at
        model.notes = entity.notes
        model.status = entity.status.value
        model.updated_by_user_id = entity.updated_by_user_id
        model.voided_by_user_id = entity.voided_by_user_id
        model.updated_at = entity.updated_at
        model.voided_at = entity.voided_at
        return model
