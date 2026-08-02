"""SQLAlchemy adapter: RecurringTransactionValidationPort."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from wealthos.modules.recurring.domain.ports.validation import TransactionSnapshot
from wealthos.modules.transactions.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)


class SqlAlchemyRecurringTransactionValidation:
    def __init__(self, session: Session) -> None:
        self._transactions = SqlAlchemyTransactionRepository(session)

    def get_transaction(
        self,
        organization_id: UUID,
        transaction_id: UUID,
    ) -> TransactionSnapshot | None:
        txn = self._transactions.get_by_id(organization_id, transaction_id)
        if txn is None:
            return None
        amount = Decimal("0.00")
        currency = "MXN"
        if txn.entries:
            amount = abs(txn.entries[0].amount.amount)
            currency = txn.entries[0].amount.currency.value
            if txn.transaction_type.is_transfer and len(txn.entries) == 2:
                credit = next(e for e in txn.entries if e.amount.amount > 0)
                amount = credit.amount.amount
                currency = credit.amount.currency.value
        return TransactionSnapshot(
            id=txn.id,
            organization_id=txn.organization_id,
            amount=amount,
            currency=currency,
            is_voided=txn.status.is_voided or txn.voided_at is not None,
        )
