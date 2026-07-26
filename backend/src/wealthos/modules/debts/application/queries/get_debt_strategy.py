"""GetDebtStrategyQuery — org payment strategy projection (orient only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.domain.services.debt_strategy_service import (
    DebtStrategyService,
    StrategyProjection,
)
from wealthos.modules.debts.domain.services.next_action_service import (
    CommitmentNextAction,
    NextActionService,
)
from wealthos.modules.organizations.domain.exceptions import OrganizationNotFoundError
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)

_ZERO = Decimal("0.00")


@dataclass(frozen=True, slots=True)
class StrategySummarySlice:
    active_commitments: int
    total_balance: Decimal
    currency: str


@dataclass(frozen=True, slots=True)
class DebtStrategyView:
    projection: StrategyProjection
    summary: StrategySummarySlice | None
    next_action: CommitmentNextAction | None
    recommended_commitment_id: UUID | None
    generated_at: datetime


class GetDebtStrategyQuery:
    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        organizations: OrganizationRepository,
        strategy_service: DebtStrategyService | None = None,
        next_action_service: NextActionService | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._organizations = organizations
        self._strategy = strategy_service or DebtStrategyService()
        self._next_action = next_action_service or NextActionService()

    def execute(
        self,
        organization_id: UUID,
        *,
        currency: str | None = None,
        today: date | None = None,
    ) -> DebtStrategyView:
        org = self._organizations.get_by_id(organization_id)
        if org is None:
            raise OrganizationNotFoundError("Organization not found.")

        today = today or date.today()
        target_currency = (currency or org.currency.value).upper()
        debts = self._debts.list_by_organization(organization_id, include_archived=False)
        balances: dict[UUID, Decimal] = {}
        for debt in debts:
            account = self._accounts.get_by_id(organization_id, debt.account_id)
            balances[debt.account_id] = (
                account.current_balance.amount if account is not None else _ZERO
            )

        projection = self._strategy.project(
            strategy=org.debt_strategy,
            debts=debts,
            balances_by_account=balances,
            today=today,
            currency=target_currency,
        )

        currency_debts = [d for d in debts if d.currency == target_currency]
        active = [
            d
            for d in currency_debts
            if d.status.is_active and balances.get(d.account_id, _ZERO) < _ZERO
        ]
        total = sum(
            (abs(balances[d.account_id]) for d in active if balances[d.account_id] < _ZERO),
            start=_ZERO,
        )
        summary = StrategySummarySlice(
            active_commitments=len(active),
            total_balance=total,
            currency=target_currency,
        )

        next_action: CommitmentNextAction | None = None
        recommended = projection.recommended_commitment_id
        if recommended is not None:
            debt = next((d for d in debts if d.id == recommended), None)
            if debt is not None:
                next_action = self._next_action.for_debt(
                    debt,
                    account_balance=balances.get(debt.account_id, _ZERO),
                    today=today,
                    is_strategy_priority=True,
                    strategy=org.debt_strategy,
                )

        return DebtStrategyView(
            projection=projection,
            summary=summary if currency_debts else None,
            next_action=next_action,
            recommended_commitment_id=recommended,
            generated_at=datetime.now(UTC),
        )
