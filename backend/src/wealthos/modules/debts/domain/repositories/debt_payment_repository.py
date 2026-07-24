"""Persistence port for DebtPayment records."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment


class DebtPaymentRepository(Protocol):
    def add(self, payment: DebtPayment) -> DebtPayment: ...

    def list_by_debt(
        self,
        organization_id: UUID,
        debt_id: UUID,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[DebtPayment], int]: ...
