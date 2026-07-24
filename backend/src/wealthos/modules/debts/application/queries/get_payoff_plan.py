"""GetPayoffPlanQuery — per-currency strategy simulation across active debts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.application.services.debt_strategy_simulator import (
    DebtStrategySimulator,
    StrategyDebtState,
    StrategyPlanResult,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository


class GetPayoffPlanQuery:
    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        simulator: DebtStrategySimulator | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._simulator = simulator or DebtStrategySimulator()

    def execute(
        self,
        organization_id: UUID,
        *,
        strategy: str,
        extra_monthly_payment: Decimal = Decimal("0"),
    ) -> list[StrategyPlanResult]:
        active_debts = self._debts.list_by_organization(organization_id, status="active")

        by_currency: dict[str, list[StrategyDebtState]] = {}
        for debt in active_debts:
            account = self._accounts.get_by_id(organization_id, debt.account_id)
            if account is None:
                continue
            currency = debt.minimum_payment.currency.value
            by_currency.setdefault(currency, []).append(
                StrategyDebtState(
                    debt_id=debt.id,
                    name=debt.name.value,
                    balance=abs(account.current_balance.amount),
                    annual_interest_rate=debt.annual_interest_rate.annual_percentage,
                    minimum_payment=debt.minimum_payment.amount,
                )
            )

        return [
            self._simulator.simulate(
                strategy=strategy,
                currency=currency,
                debts=by_currency[currency],
                extra_monthly_payment=extra_monthly_payment,
            )
            for currency in sorted(by_currency)
        ]
