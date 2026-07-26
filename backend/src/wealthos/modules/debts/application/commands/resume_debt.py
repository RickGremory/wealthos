"""ResumeDebt command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.domain.exceptions import DebtNotFoundError
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository


@dataclass(frozen=True, slots=True)
class ResumeDebtInput:
    organization_id: UUID
    debt_id: UUID


class ResumeDebtCommand:
    def __init__(self, debts: DebtRepository) -> None:
        self._debts = debts

    def execute(self, data: ResumeDebtInput) -> Debt:
        debt = self._debts.get_by_id(data.organization_id, data.debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")
        debt.resume()
        return self._debts.save(debt)
