"""GetDebtQuery — attach account balance + payoff projection to a single debt."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.application.services.debt_payoff_calculator import (
    DebtPayoffCalculator,
)
from wealthos.modules.debts.application.views.debt_view import (
    DebtWithBalance,
    build_debt_with_balance,
)
from wealthos.modules.debts.domain.exceptions import DebtNotFoundError
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.domain.services.debt_state_service import DebtStateService


class GetDebtQuery:
    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        calculator: DebtPayoffCalculator | None = None,
        state_service: DebtStateService | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._calculator = calculator or DebtPayoffCalculator()
        self._state_service = state_service or DebtStateService()

    def execute(self, organization_id: UUID, debt_id: UUID) -> DebtWithBalance:
        debt = self._debts.get_by_id(organization_id, debt_id)
        if debt is None:
            raise DebtNotFoundError("Debt not found.")
        account = self._accounts.get_by_id(organization_id, debt.account_id)
        return build_debt_with_balance(
            debt,
            account,
            self._calculator,
            state_service=self._state_service,
        )
