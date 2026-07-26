"""Commitments (debts) → confirmed outflows for the projection window."""

from __future__ import annotations

from datetime import UTC, datetime, time
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.debts.domain.repositories.debt_repository import DebtRepository
from wealthos.modules.debts.domain.services.debt_state_service import (
    DebtStateService,
    next_due_date_on_or_after,
)
from wealthos.modules.planning.domain.enums.cash_flow import (
    CashFlowCertainty,
    CashFlowDirection,
    CashFlowStatus,
)
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.cash_flow import PlanningCashFlow
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.money_utils import quantize_money
from wealthos.modules.planning.domain.value_objects.source_reference import (
    PlanningSourceReference,
)


class CommitmentsPlanningAdapter:
    source_name = PlanningSource.COMMITMENTS.value

    def __init__(
        self,
        debts: DebtRepository,
        accounts: AccountRepository,
        state_service: DebtStateService | None = None,
    ) -> None:
        self._debts = debts
        self._accounts = accounts
        self._state = state_service or DebtStateService()

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        currency = request.currency.strip().upper()
        try:
            zone = ZoneInfo(request.timezone)
        except Exception:
            zone = ZoneInfo("UTC")

        local_start = request.period_start.astimezone(zone).date()
        local_end = request.period_end.astimezone(zone).date()
        flows: list[PlanningCashFlow] = []

        account_balances: dict[UUID, Decimal] = {}
        for account in self._accounts.list_by_organization(
            request.organization_id,
            include_archived=True,
        ):
            account_balances[account.id] = account.current_balance.amount

        for debt in self._debts.list_by_organization(
            request.organization_id,
            include_archived=False,
        ):
            if debt.currency.strip().upper() != currency:
                continue
            if debt.status.is_archived or debt.status.is_closed:
                continue
            if debt.due_day is None:
                continue

            payment = debt.scheduled_payment or debt.minimum_payment
            if payment is None or payment.amount <= Decimal("0"):
                continue

            balance = account_balances.get(debt.account_id, Decimal("0"))
            snap = self._state.snapshot(debt, account_balance=balance, today=local_start)
            due = snap.next_due_date
            if due is None:
                due = next_due_date_on_or_after(due_day=debt.due_day, on_or_after=local_start)
            if due < local_start or due > local_end:
                continue

            amount = quantize_money(payment.amount)
            due_at = datetime.combine(due, time.min, tzinfo=zone)
            key = f"commitment:{debt.id}:due:{due.isoformat()}"
            flows.append(
                PlanningCashFlow(
                    id=key,
                    organization_id=request.organization_id,
                    direction=CashFlowDirection.OUTFLOW,
                    amount=amount,
                    outstanding_amount=amount,
                    currency=currency,
                    expected_at=due_at,
                    certainty=CashFlowCertainty.CONFIRMED,
                    status=CashFlowStatus.ACTIVE,
                    category="commitment",
                    label=str(debt.name),
                    source=PlanningSourceReference(
                        source_name=self.source_name,
                        resource_type="debt",
                        resource_id=str(debt.id),
                        occurrence_key=key,
                        resource_version=debt.version,
                    ),
                )
            )

        return PlanningSourceContribution(
            source_name=self.source_name,
            cash_flows=tuple(flows),
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=now,
                status=SourceStatus.AVAILABLE,
            ),
        )
