"""Application port for posting expenses without coupling to Transactions infra."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.transactions.application.commands.create_expense import (
    CreateExpenseCommand,
    CreateExpenseInput,
)
from wealthos.shared.domain.value_objects.money import Money


class FinancialExpenseService(Protocol):
    def create_expense(
        self,
        *,
        organization_id: UUID,
        account_id: UUID,
        category_id: UUID,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        notes: str | None = None,
    ) -> UUID: ...


class CreateExpenseFinancialExpenseService:
    """Adapter over CreateExpenseCommand."""

    def __init__(self, command: CreateExpenseCommand) -> None:
        self._command = command

    def create_expense(
        self,
        *,
        organization_id: UUID,
        account_id: UUID,
        category_id: UUID,
        amount: Money,
        description: str,
        occurred_at: datetime,
        created_by_user_id: UUID,
        notes: str | None = None,
    ) -> UUID:
        transaction = self._command.execute(
            CreateExpenseInput(
                organization_id=organization_id,
                account_id=account_id,
                category_id=category_id,
                amount=amount.amount,
                description=description,
                occurred_at=occurred_at,
                created_by_user_id=created_by_user_id,
                notes=notes,
            )
        )
        return transaction.id
