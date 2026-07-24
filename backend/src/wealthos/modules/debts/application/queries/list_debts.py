"""ListDebtsQuery — attach account balances + payoff projections for many debts."""

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
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository


class ListDebtsQuery:
    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        calculator: DebtPayoffCalculator | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._calculator = calculator or DebtPayoffCalculator()

    def execute(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        debt_type: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[DebtWithBalance]:
        debts = self._debts.list_by_organization(
            organization_id,
            status=status,
            debt_type=debt_type,
            currency=currency,
            include_archived=include_archived,
        )
        items: list[DebtWithBalance] = []
        for debt in debts:
            account = self._accounts.get_by_id(organization_id, debt.account_id)
            items.append(build_debt_with_balance(debt, account, self._calculator))
        return items
