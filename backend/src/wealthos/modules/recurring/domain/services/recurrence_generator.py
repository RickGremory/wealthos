"""Pure, deterministic RecurrenceGenerator (SPEC-005 / Sprint 9.2)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Sequence
from zoneinfo import ZoneInfo

from wealthos.modules.recurring.domain.entities.occurrence_exception import (
    RecurringOccurrenceException,
)
from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.entities.recurring_rule import RecurringRule
from wealthos.modules.recurring.domain.entities.recurring_rule_pause import (
    RecurringRulePause,
)
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringExceptionType
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringCertainty,
    RecurringRuleStatus,
)
from wealthos.modules.recurring.domain.exceptions import (
    InvalidRecurrenceRange,
    RecurrenceOccurrenceLimitExceeded,
    RecurrenceRangeTooLarge,
)
from wealthos.modules.recurring.domain.services.occurrence_status_resolver import (
    OccurrenceStatusResolver,
)
from wealthos.modules.recurring.domain.services.pause_normalizer import PauseNormalizer
from wealthos.modules.recurring.domain.services.recurrence_strategies import strategy_for
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey
from wealthos.modules.recurring.domain.value_objects.recurring_occurrence import (
    RecurringOccurrence,
)

MAX_GENERATION_DAYS = 366
MAX_OCCURRENCES_PER_REQUEST = 1_000


@dataclass(frozen=True, slots=True)
class _Draft:
    key: OccurrenceKey
    original_expected_on: date
    expected_on: date
    base_amount: Decimal
    expected_amount: Decimal
    certainty: RecurringCertainty
    is_exception: bool
    exception_id: object | None
    skipped: bool


class DefaultRecurrenceGenerator:
    """Generate occurrences for one rule version within a bounded period."""

    def __init__(
        self,
        *,
        pause_normalizer: PauseNormalizer | None = None,
        status_resolver: OccurrenceStatusResolver | None = None,
    ) -> None:
        self._pauses = pause_normalizer or PauseNormalizer()
        self._status = status_resolver or OccurrenceStatusResolver()

    def generate(
        self,
        *,
        rule: RecurringRule,
        version: RecurringRuleVersion,
        period_start: date,
        period_end: date,
        pauses: Sequence[RecurringRulePause] = (),
        exceptions: Sequence[RecurringOccurrenceException] = (),
        settlements: Sequence[RecurringOccurrenceSettlement] = (),
        evaluated_on: date,
        timezone: str,
    ) -> tuple[RecurringOccurrence, ...]:
        self._validate_request(period_start=period_start, period_end=period_end)

        if rule.status in {RecurringRuleStatus.ARCHIVED, RecurringRuleStatus.ENDED}:
            return ()

        effective_start = max(period_start, version.starts_on, version.effective_from)
        effective_end_candidates = [period_end]
        if version.ends_on is not None:
            effective_end_candidates.append(version.ends_on)
        if version.effective_until is not None:
            effective_end_candidates.append(version.effective_until)
        effective_end = min(effective_end_candidates)
        if effective_start > effective_end:
            return ()

        base_dates = strategy_for(version.pattern.frequency).generate_base_dates(
            version=version,
            effective_start=effective_start,
            effective_end=effective_end,
        )

        pause_ranges = self._pauses.normalize(pauses)
        active_exceptions = {
            item.original_occurrence_key: item
            for item in exceptions
            if item.is_active
        }
        settlements_by_key: dict[str, list[RecurringOccurrenceSettlement]] = {}
        for settlement in settlements:
            if settlement.is_voided:
                continue
            settlements_by_key.setdefault(settlement.occurrence_key, []).append(settlement)

        drafts: list[_Draft] = []
        seen_keys: set[str] = set()

        for base_date in base_dates:
            key = OccurrenceKey.for_recurring_rule(rule.id, base_date)
            if self._pauses.contains(pause_ranges, base_date):
                continue
            exception = active_exceptions.get(key.value)
            draft = self._draft_from_base(
                version=version,
                base_date=base_date,
                key=key,
                exception=exception,
            )
            drafts.append(draft)
            seen_keys.add(key.value)

        # Occurrences moved into range from outside base generation.
        for exception in active_exceptions.values():
            if exception.original_occurrence_key in seen_keys:
                continue
            if exception.exception_type is RecurringExceptionType.SKIP:
                continue
            replacement = exception.replacement_expected_on
            if replacement is None:
                continue
            if not (period_start <= replacement <= period_end):
                continue
            if self._pauses.contains(pause_ranges, exception.original_expected_on):
                continue
            key = OccurrenceKey(exception.original_occurrence_key)
            draft = self._draft_from_base(
                version=version,
                base_date=exception.original_expected_on,
                key=key,
                exception=exception,
            )
            drafts.append(draft)

        tz = ZoneInfo(timezone)
        results: list[RecurringOccurrence] = []
        for draft in drafts:
            if not (period_start <= draft.expected_on <= period_end):
                continue
            linked = settlements_by_key.get(draft.key.value, [])
            status = self._status.resolve(
                expected_on=draft.expected_on,
                evaluated_on=evaluated_on,
                grace_period_days=version.grace_period_days,
                skipped=draft.skipped,
                cancelled=False,
                expected_amount=draft.expected_amount,
                settlement_mode=version.settlement_mode,
                settlements=linked,
            )
            actual = sum((item.settled_amount for item in linked), Decimal("0")) or None
            if linked and actual == 0:
                actual = None
            if linked:
                actual = sum((item.settled_amount for item in linked), Decimal("0"))
            variance = (
                (actual - draft.expected_amount) if actual is not None else None
            )
            results.append(
                RecurringOccurrence(
                    occurrence_key=draft.key,
                    recurring_rule_id=rule.id,
                    organization_id=rule.organization_id,
                    original_expected_on=draft.original_expected_on,
                    expected_on=draft.expected_on,
                    expected_at=datetime.combine(draft.expected_on, time.min, tzinfo=tz),
                    direction=version.direction,
                    base_amount=draft.base_amount,
                    expected_amount=draft.expected_amount,
                    currency=version.currency,
                    certainty=draft.certainty,
                    status=status,
                    category_id=version.category_id,
                    account_id=version.account_id,
                    destination_account_id=version.destination_account_id,
                    is_exception=draft.is_exception,
                    exception_id=draft.exception_id,  # type: ignore[arg-type]
                    related_transaction_ids=tuple(item.transaction_id for item in linked),
                    actual_amount=actual,
                    variance_amount=variance,
                )
            )

        ordered = tuple(
            sorted(
                results,
                key=lambda item: (item.expected_on, item.occurrence_key.value),
            )
        )
        if len(ordered) > MAX_OCCURRENCES_PER_REQUEST:
            raise RecurrenceOccurrenceLimitExceeded(
                f"Generation produced more than {MAX_OCCURRENCES_PER_REQUEST} occurrences."
            )
        return ordered

    def _validate_request(self, *, period_start: date, period_end: date) -> None:
        if period_start > period_end:
            raise InvalidRecurrenceRange("period_start must be <= period_end.")
        span = (period_end - period_start).days + 1
        if span > MAX_GENERATION_DAYS:
            raise RecurrenceRangeTooLarge(
                f"Requested period exceeds {MAX_GENERATION_DAYS} days."
            )

    def _draft_from_base(
        self,
        *,
        version: RecurringRuleVersion,
        base_date: date,
        key: OccurrenceKey,
        exception: RecurringOccurrenceException | None,
    ) -> _Draft:
        expected_on = base_date
        expected_amount = version.amount
        certainty = version.certainty
        skipped = False
        is_exception = False
        exception_id = None
        if exception is not None:
            is_exception = True
            exception_id = exception.id
            if exception.exception_type is RecurringExceptionType.SKIP:
                skipped = True
            else:
                if exception.replacement_expected_on is not None:
                    expected_on = exception.replacement_expected_on
                if exception.replacement_amount is not None:
                    expected_amount = exception.replacement_amount
                if exception.replacement_certainty is not None:
                    certainty = exception.replacement_certainty
        return _Draft(
            key=key,
            original_expected_on=base_date,
            expected_on=expected_on,
            base_amount=version.amount,
            expected_amount=expected_amount,
            certainty=certainty,
            is_exception=is_exception,
            exception_id=exception_id,
            skipped=skipped,
        )
