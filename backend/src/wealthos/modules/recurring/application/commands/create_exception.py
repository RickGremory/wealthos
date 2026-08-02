"""Create / deactivate occurrence exceptions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.recurring.application.commands._helpers import (
    ensure_expected_version,
    ensure_manual_writable,
    load_aggregate,
)
from wealthos.modules.recurring.domain.entities.occurrence_exception import (
    RecurringOccurrenceException,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringExceptionType
from wealthos.modules.recurring.domain.enums.rule import RecurringCertainty
from wealthos.modules.recurring.domain.exceptions import (
    OccurrenceAlreadySettled,
    OccurrenceAlreadySkipped,
    OccurrenceNotFound,
    RecurringError,
)
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringAggregateRepository,
    RecurringSettlementRepository,
)
from wealthos.modules.recurring.domain.services.recurrence_generator import (
    DefaultRecurrenceGenerator,
)


@dataclass(frozen=True, slots=True)
class CreateRecurringOccurrenceExceptionCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    occurrence_key: str
    exception_type: RecurringExceptionType
    expected_version: int
    evaluated_on: date
    timezone: str
    replacement_expected_on: date | None = None
    replacement_amount: Decimal | None = None
    replacement_certainty: RecurringCertainty | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class DeactivateRecurringOccurrenceExceptionCommand:
    organization_id: UUID
    actor_id: UUID
    rule_id: UUID
    exception_id: UUID
    expected_version: int


class CreateRecurringOccurrenceExceptionHandler:
    def __init__(
        self,
        repo: RecurringAggregateRepository,
        settlements: RecurringSettlementRepository | None = None,
        generator: DefaultRecurrenceGenerator | None = None,
    ) -> None:
        self._repo = repo
        self._settlements = settlements
        self._generator = generator or DefaultRecurrenceGenerator()

    def execute(
        self,
        command: CreateRecurringOccurrenceExceptionCommand,
    ) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)

        original_on = self._parse_original_date(command.occurrence_key, aggregate.id)
        version = aggregate.current_version(original_on)
        if version is None:
            raise OccurrenceNotFound("No effective version covers this occurrence.")

        occurrences = self._generator.generate(
            rule=aggregate.rule,
            version=version,
            period_start=original_on,
            period_end=original_on,
            pauses=tuple(aggregate.pauses),
            exceptions=(),
            settlements=(),
            evaluated_on=command.evaluated_on,
            timezone=command.timezone,
        )
        if not any(item.occurrence_key.value == command.occurrence_key for item in occurrences):
            raise OccurrenceNotFound(
                "Occurrence key does not match a generated occurrence for this rule."
            )

        if self._settlements is not None:
            linked = self._settlements.list_for_occurrence(
                command.organization_id,
                command.occurrence_key,
            )
            if linked and command.exception_type in {
                RecurringExceptionType.SKIP,
                RecurringExceptionType.RESCHEDULE,
            }:
                raise OccurrenceAlreadySettled(
                    "Cannot skip or reschedule a settled occurrence."
                )

        for existing in aggregate.active_exceptions():
            if existing.original_occurrence_key == command.occurrence_key:
                if existing.exception_type is RecurringExceptionType.SKIP:
                    raise OccurrenceAlreadySkipped("Occurrence is already skipped.")
                break

        exception = RecurringOccurrenceException(
            organization_id=aggregate.organization_id,
            recurring_rule_id=aggregate.id,
            original_occurrence_key=command.occurrence_key,
            original_expected_on=original_on,
            exception_type=command.exception_type,
            replacement_expected_on=command.replacement_expected_on,
            replacement_amount=command.replacement_amount,
            replacement_certainty=command.replacement_certainty,
            reason=command.reason,
            created_by=command.actor_id,
        )
        aggregate.add_exception(exception)
        return self._repo.save(aggregate, command.expected_version)

    @staticmethod
    def _parse_original_date(occurrence_key: str, rule_id: UUID) -> date:
        prefix = f"recurring:{rule_id}:occurrence:"
        if not occurrence_key.startswith(prefix):
            raise OccurrenceNotFound("Invalid occurrence key for this rule.")
        try:
            return date.fromisoformat(occurrence_key.removeprefix(prefix))
        except ValueError as exc:
            raise OccurrenceNotFound("Invalid occurrence key date.") from exc


class DeactivateRecurringOccurrenceExceptionHandler:
    def __init__(self, repo: RecurringAggregateRepository) -> None:
        self._repo = repo

    def execute(
        self,
        command: DeactivateRecurringOccurrenceExceptionCommand,
    ) -> RecurringAggregate:
        aggregate = load_aggregate(
            self._repo,
            organization_id=command.organization_id,
            rule_id=command.rule_id,
            for_update=True,
        )
        ensure_manual_writable(aggregate)
        ensure_expected_version(aggregate, command.expected_version)

        target = next(
            (item for item in aggregate.exceptions if item.id == command.exception_id),
            None,
        )
        if target is None:
            raise RecurringError(
                "Exception not found.",
                code="occurrence_not_found",
            )
        if target.is_active:
            target.deactivate()
            aggregate.rule.touch()
        return self._repo.save(aggregate, command.expected_version)
