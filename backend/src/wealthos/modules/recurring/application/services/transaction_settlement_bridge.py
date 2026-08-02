"""Bridge Transaction create/void ↔ Recurring settlements (SPEC-005 PR5)."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from wealthos.modules.recurring.application.commands.link_transaction import (
    LinkRecurringOccurrenceTransactionCommand,
    LinkRecurringOccurrenceTransactionHandler,
)
from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringSettlementLinkType
from wealthos.modules.recurring.domain.exceptions import OccurrenceNotFound, RecurringError
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringSettlementRepository,
)
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey
from wealthos.modules.transactions.domain.entities.transaction import Transaction

RECURRING_OCCURRENCE_SOURCE = "recurring_occurrence"


def parse_rule_id_from_occurrence_key(occurrence_key: str) -> UUID:
    """Extract rule id from `recurring:{uuid}:occurrence:{YYYY-MM-DD}`."""
    parts = occurrence_key.split(":")
    if len(parts) != 4 or parts[0] != "recurring" or parts[2] != "occurrence":
        raise OccurrenceNotFound("Invalid recurring occurrence key.")
    try:
        return UUID(parts[1])
    except ValueError as exc:
        raise OccurrenceNotFound("Invalid recurring occurrence key.") from exc


class RecurringTransactionSettlementBridge:
    """Atomic confirm/link helpers used from Transactions write paths."""

    def __init__(
        self,
        link_handler: LinkRecurringOccurrenceTransactionHandler,
        settlements: RecurringSettlementRepository,
    ) -> None:
        self._link = link_handler
        self._settlements = settlements

    def link_from_posted_transaction(
        self,
        *,
        transaction: Transaction,
        actor_id: UUID,
        timezone: str,
        evaluated_on: date | None = None,
        link_type: RecurringSettlementLinkType = RecurringSettlementLinkType.EXPLICIT,
    ) -> RecurringOccurrenceSettlement | None:
        if transaction.source_type != RECURRING_OCCURRENCE_SOURCE:
            return None
        key = transaction.source_occurrence_key
        if not key:
            raise RecurringError(
                "source_occurrence_key is required for recurring_occurrence source.",
                code="invalid_occurrence_key",
            )
        rule_id = parse_rule_id_from_occurrence_key(key)
        if (
            transaction.related_resource_id is not None
            and transaction.related_resource_id != rule_id
        ):
            raise RecurringError(
                "related_resource_id does not match occurrence key rule.",
                code="invalid_occurrence_key",
            )
        # Ensure key uses canonical format for this rule id
        _ = OccurrenceKey(key)

        return self._link.execute(
            LinkRecurringOccurrenceTransactionCommand(
                organization_id=transaction.organization_id,
                actor_id=actor_id,
                rule_id=rule_id,
                occurrence_key=key,
                transaction_id=transaction.id,
                link_type=link_type,
                evaluated_on=evaluated_on or date.today(),
                timezone=timezone,
            )
        )

    def void_settlements_for_transaction(
        self,
        *,
        organization_id: UUID,
        transaction_id: UUID,
    ) -> list[RecurringOccurrenceSettlement]:
        active = self._settlements.list_for_transaction(
            organization_id,
            transaction_id,
            include_voided=False,
        )
        voided: list[RecurringOccurrenceSettlement] = []
        for settlement in active:
            settlement.void()
            voided.append(self._settlements.save(settlement))
        return voided
