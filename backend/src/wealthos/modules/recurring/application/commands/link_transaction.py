"""Link / unlink transactions to recurring occurrences."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.application.commands._helpers import load_aggregate
from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringExceptionType
from wealthos.modules.recurring.domain.enums.occurrence import RecurringSettlementLinkType
from wealthos.modules.recurring.domain.exceptions import (
    OccurrenceAlreadySkipped,
    OccurrenceNotFound,
    RecurringError,
    TransactionAlreadyLinked,
    TransactionNotFound,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringSettlementRepository,
)
from wealthos.modules.recurring.domain.ports.validation import (
    RecurringTransactionValidationPort,
)
from wealthos.modules.recurring.domain.services.recurrence_generator import (
    DefaultRecurrenceGenerator,
)


@dataclass(frozen=True, slots=True)
class LinkRecurringOccurrenceTransactionCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    occurrence_key: str
    transaction_id: UUID
    link_type: RecurringSettlementLinkType
    evaluated_on: date
    timezone: str
    settled_amount: Decimal | None = None


@dataclass(frozen=True, slots=True)
class UnlinkRecurringOccurrenceTransactionCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    settlement_id: UUID


class LinkRecurringOccurrenceTransactionHandler:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository,
        transactions: RecurringTransactionValidationPort,
        generator: DefaultRecurrenceGenerator | None = None,
    ) -> None:
        self._repo = repo
        self._settlements = settlements
        self._transactions = transactions
        self._generator = generator or DefaultRecurrenceGenerator()

    def execute(
        self,
        command: LinkRecurringOccurrenceTransactionCommand,
    ) -> RecurringOccurrenceSettlement:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
        )
        for exception in aggregate.active_exceptions():
            if (
                exception.original_occurrence_key == command.occurrence_key
                and exception.exception_type is RecurringExceptionType.SKIP
            ):
                raise OccurrenceAlreadySkipped(
                    "Cannot link a transaction to a skipped occurrence."
                )

        original_on = _parse_original_date(command.occurrence_key, aggregate.id)
        version = aggregate.current_version(original_on)
        if version is None:
            raise OccurrenceNotFound("No effective version covers this occurrence.")

        generated = self._generator.generate(
            rule=aggregate.rule,
            version=version,
            period_start=original_on,
            period_end=original_on,
            pauses=tuple(aggregate.pauses),
            exceptions=tuple(aggregate.active_exceptions()),
            settlements=(),
            evaluated_on=command.evaluated_on,
            timezone=command.timezone,
        )
        if not any(item.occurrence_key.value == command.occurrence_key for item in generated):
            raise OccurrenceNotFound(
                "Occurrence key does not match a generated occurrence for this rule."
            )

        txn = self._transactions.get_transaction(
            command.organization_id,
            command.transaction_id,
        )
        if txn is None or txn.is_voided:
            raise TransactionNotFound("Transaction not found or voided.")
        if txn.currency.upper() != version.currency.upper():
            raise RecurringError(
                "Transaction currency does not match the recurring rule.",
                code="transaction_currency_mismatch",
            )

        existing = self._settlements.list_for_occurrence(
            command.organization_id,
            command.occurrence_key,
            include_voided=True,
        )
        for item in existing:
            if item.transaction_id == command.transaction_id and not item.is_voided:
                raise TransactionAlreadyLinked(
                    "Transaction is already linked to this occurrence."
                )

        amount = command.settled_amount or txn.amount
        settlement = RecurringOccurrenceSettlement(
            organization_id=command.organization_id,
            recurring_rule_id=aggregate.id,
            occurrence_key=command.occurrence_key,
            transaction_id=command.transaction_id,
            settled_amount=amount,
            link_type=command.link_type,
            linked_by=command.actor_id,
        )
        return self._settlements.add(settlement)


class UnlinkRecurringOccurrenceTransactionHandler:
    def __init__(self, settlements: RecurringSettlementRepository) -> None:
        self._settlements = settlements

    def execute(
        self,
        command: UnlinkRecurringOccurrenceTransactionCommand,
    ) -> RecurringOccurrenceSettlement:
        settlement = self._settlements.get_by_id(
            command.organization_id,
            command.settlement_id,
        )
        if settlement is None or settlement.recurring_rule_id != command.rule_id:
            raise RecurringError(
                "Settlement not found.",
                code="occurrence_not_found",
            )
        settlement.void()
        return self._settlements.save(settlement)


def _parse_original_date(occurrence_key: str, rule_id: UUID) -> date:
    prefix = f"recurring:{rule_id}:occurrence:"
    if not occurrence_key.startswith(prefix):
        raise OccurrenceNotFound("Invalid occurrence key for this rule.")
    try:
        return date.fromisoformat(occurrence_key.removeprefix(prefix))
    except ValueError as exc:
        raise OccurrenceNotFound("Invalid occurrence key date.") from exc
