"""ListDebtPaymentsQuery — paginated payment history for a debt."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt_payment import DebtPayment
from wealthos.modules.debts.domain.exceptions import DebtNotFoundError
from wealthos.modules.debts.domain.repositories.debt_payment_repository import (
    DebtPaymentRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository


@dataclass(frozen=True, slots=True)
class DebtPaymentsResult:
    items: list[DebtPayment]
    total: int


class ListDebtPaymentsQuery:
    def __init__(self, debts: DebtRepository, payments: DebtPaymentRepository) -> None:
        self._debts = debts
        self._payments = payments

    def execute(
        self,
        organization_id: UUID,
        debt_id: UUID,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> DebtPaymentsResult:
        debt = self._debts.get_by_id(organization_id, debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")
        items, total = self._payments.list_by_debt(
            organization_id,
            debt_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return DebtPaymentsResult(items=items, total=total)
