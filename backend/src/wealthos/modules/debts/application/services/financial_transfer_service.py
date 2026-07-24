"""Application port for posting transfers without coupling to Transactions infra."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.transactions.application.commands.create_transfer import (
    CreateTransferCommand,
    CreateTransferInput,
)
from wealthos.shared.domain.value_objects.money import Money


class FinancialTransferService(Protocol):
    def transfer(
        self,
        *,
        organization_id: UUID,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: Money,
        occurred_at: datetime,
        description: str,
        created_by_user_id: UUID,
        notes: str | None = None,
    ) -> UUID: ...


class CreateTransferFinancialTransferService:
    """Adapter over CreateTransferCommand."""

    def __init__(self, command: CreateTransferCommand) -> None:
        self._command = command

    def transfer(
        self,
        *,
        organization_id: UUID,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: Money,
        occurred_at: datetime,
        description: str,
        created_by_user_id: UUID,
        notes: str | None = None,
    ) -> UUID:
        transaction = self._command.execute(
            CreateTransferInput(
                organization_id=organization_id,
                source_account_id=source_account_id,
                destination_account_id=destination_account_id,
                amount=amount.amount,
                description=description,
                occurred_at=occurred_at,
                created_by_user_id=created_by_user_id,
                notes=notes,
            )
        )
        return transaction.id
