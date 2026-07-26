"""Accounts → liquid cash snapshots for Planning."""

from __future__ import annotations

from datetime import UTC, datetime

from wealthos.modules.accounts.domain.repositories.account_repository import (
    AccountRepository,
)
from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.policies.account_eligibility import (
    AccountEligibilityPolicy,
)
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.account_snapshot import (
    PlanningAccountSnapshot,
)
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.money_utils import quantize_money


class AccountsPlanningAdapter:
    source_name = PlanningSource.ACCOUNTS.value

    def __init__(
        self,
        accounts: AccountRepository,
        eligibility: AccountEligibilityPolicy | None = None,
    ) -> None:
        self._accounts = accounts
        self._eligibility = eligibility or AccountEligibilityPolicy()

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        currency = request.currency.strip().upper()
        snapshots: list[PlanningAccountSnapshot] = []

        for account in self._accounts.list_by_organization(
            request.organization_id,
            include_archived=False,
        ):
            if account.currency.value != currency:
                continue
            account_type = account.account_type.value
            reason = self._eligibility.exclusion_reason(
                account_type=account_type,
                is_active=account.is_active,
            )
            is_liquid = self._eligibility.is_liquid(account_type)
            balance = quantize_money(account.current_balance.amount)
            snapshots.append(
                PlanningAccountSnapshot(
                    account_id=account.id,
                    organization_id=account.organization_id,
                    name=str(account.name),
                    account_type=account_type,
                    currency=currency,
                    ledger_balance=balance,
                    available_balance=balance,
                    is_liquid=is_liquid,
                    is_included=reason is None,
                    exclusion_reason=reason,
                    balance_as_of=account.updated_at,
                )
            )

        return PlanningSourceContribution(
            source_name=self.source_name,
            accounts=tuple(snapshots),
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=max((s.balance_as_of for s in snapshots), default=now),
                status=SourceStatus.AVAILABLE,
            ),
        )
