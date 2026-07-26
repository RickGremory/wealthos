"""Transactions → settlements when an occurrence_key is present."""

from __future__ import annotations

from datetime import UTC, datetime

from wealthos.modules.planning.domain.enums.source import PlanningSource, SourceStatus
from wealthos.modules.planning.domain.ports.source_adapter import (
    PlanningCollectionRequest,
    PlanningSourceContribution,
)
from wealthos.modules.planning.domain.value_objects.collection_warning import (
    PlanningSourceMetadata,
)
from wealthos.modules.planning.domain.value_objects.settlement import PlanningSettlement


class TransactionsPlanningAdapter:
    """V1: only explicit occurrence_key settlements (no heuristic matching)."""

    source_name = PlanningSource.TRANSACTIONS.value

    def __init__(self, transactions: object | None = None) -> None:
        self._transactions = transactions

    def collect(self, request: PlanningCollectionRequest) -> PlanningSourceContribution:
        now = datetime.now(UTC)
        settlements: list[PlanningSettlement] = []

        list_fn = getattr(self._transactions, "list_with_occurrence_keys", None)
        if callable(list_fn):
            for item in list_fn(
                request.organization_id,
                currency=request.currency,
                date_from=request.period_start,
                date_to=request.period_end,
            ):
                settlements.append(
                    PlanningSettlement(
                        transaction_id=item.transaction_id,
                        organization_id=request.organization_id,
                        amount=item.amount,
                        currency=item.currency,
                        settled_at=item.settled_at,
                        source_occurrence_key=item.occurrence_key,
                        related_resource_type=getattr(item, "related_resource_type", None),
                        related_resource_id=getattr(item, "related_resource_id", None),
                    )
                )

        return PlanningSourceContribution(
            source_name=self.source_name,
            settlements=tuple(settlements),
            metadata=PlanningSourceMetadata(
                source_name=self.source_name,
                collected_at=now,
                data_as_of=now,
                status=SourceStatus.AVAILABLE,
            ),
        )
