"""PauseDebt command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import DebtNotFoundError
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository


@dataclass(frozen=True, slots=True)
class PauseDebtInput:
    organization_id: UUID
    debt_id: UUID


class PauseDebtCommand:
    def __init__(self, debts: DebtRepository) -> None:
        self._debts = debts

    def execute(self, data: PauseDebtInput) -> Debt:
        debt = self._debts.get_by_id(data.organization_id, data.debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")
        debt.pause()
        return self._debts.save(debt)
