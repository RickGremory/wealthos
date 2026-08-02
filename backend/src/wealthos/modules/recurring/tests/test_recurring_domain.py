"""Domain tests for Recurring PR1 (pattern, aggregate, keys)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from wealthos.modules.recurring.domain.entities.occurrence_exception import (
    RecurringOccurrenceException,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.entities.recurring_rule import RecurringRule
from wealthos.modules.recurring.domain.entities.recurring_rule_pause import (
    RecurringRulePause,
)
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringExceptionType
from wealthos.modules.recurring.domain.enums.recurrence import (
    RecurrenceFrequency,
    Weekday,
)
from wealthos.modules.recurring.domain.enums.rule import RecurringDirection
from wealthos.modules.recurring.domain.exceptions import (
    DuplicateOccurrenceException,
    InvalidRecurrencePattern,
    PauseAlreadyOpen,
    RecurringVersionOverlap,
)
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


def _monthly_version(
    rule: RecurringRule,
    *,
    effective_from: date,
    amount: str = "800.00",
    effective_until: date | None = None,
) -> RecurringRuleVersion:
    return RecurringRuleVersion(
        recurring_rule_id=rule.id,
        organization_id=rule.organization_id,
        effective_from=effective_from,
        effective_until=effective_until,
        name="Internet",
        direction=RecurringDirection.OUTFLOW,
        amount=Decimal(amount),
        currency="MXN",
        pattern=RecurrencePattern(
            frequency=RecurrenceFrequency.MONTHLY,
            interval=1,
            day_of_month=15,
        ),
        starts_on=effective_from,
    )


def test_occurrence_key_is_stable() -> None:
    rule_id = uuid4()
    key = OccurrenceKey.for_recurring_rule(rule_id, date(2026, 8, 15))
    assert key.value == f"recurring:{rule_id}:occurrence:2026-08-15"


def test_weekly_pattern_normalizes_days() -> None:
    pattern = RecurrencePattern(
        frequency=RecurrenceFrequency.WEEKLY,
        interval=1,
        days_of_week=(Weekday.THURSDAY, Weekday.MONDAY, Weekday.THURSDAY),
    )
    assert pattern.days_of_week == (Weekday.MONDAY, Weekday.THURSDAY)


def test_monthly_requires_day_or_end() -> None:
    with pytest.raises(InvalidRecurrencePattern):
        RecurrencePattern(frequency=RecurrenceFrequency.MONTHLY, interval=1)


def test_aggregate_rejects_overlapping_versions() -> None:
    rule = RecurringRule(organization_id=uuid4())
    aggregate = RecurringAggregate(
        rule=rule,
        versions=[_monthly_version(rule, effective_from=date(2026, 1, 1))],
    )
    with pytest.raises(RecurringVersionOverlap):
        aggregate.add_version(
            _monthly_version(
                rule,
                effective_from=date(2026, 6, 1),
                amount="950.00",
            )
        )


def test_close_current_and_add_version() -> None:
    rule = RecurringRule(organization_id=uuid4())
    aggregate = RecurringAggregate(
        rule=rule,
        versions=[_monthly_version(rule, effective_from=date(2026, 1, 1))],
    )
    expected = rule.version
    aggregate.close_current_and_add_version(
        effective_from=date(2026, 9, 1),
        new_version=_monthly_version(
            rule,
            effective_from=date(2026, 9, 1),
            amount="950.00",
        ),
    )
    assert aggregate.versions[0].effective_until == date(2026, 8, 31)
    assert aggregate.current_version(date(2026, 8, 15)).amount == Decimal("800.00")
    assert aggregate.current_version(date(2026, 9, 15)).amount == Decimal("950.00")
    assert aggregate.version == expected + 1


def test_pause_open_uniqueness() -> None:
    rule = RecurringRule(organization_id=uuid4())
    aggregate = RecurringAggregate(rule=rule, versions=[
        _monthly_version(rule, effective_from=date(2026, 1, 1)),
    ])
    aggregate.add_pause(
        RecurringRulePause(
            recurring_rule_id=rule.id,
            organization_id=rule.organization_id,
            starts_on=date(2026, 8, 1),
        )
    )
    with pytest.raises(PauseAlreadyOpen):
        aggregate.add_pause(
            RecurringRulePause(
                recurring_rule_id=rule.id,
                organization_id=rule.organization_id,
                starts_on=date(2026, 9, 1),
            )
        )


def test_resume_closes_day_before() -> None:
    rule = RecurringRule(organization_id=uuid4())
    aggregate = RecurringAggregate(rule=rule, versions=[
        _monthly_version(rule, effective_from=date(2026, 1, 1)),
    ])
    aggregate.add_pause(
        RecurringRulePause(
            recurring_rule_id=rule.id,
            organization_id=rule.organization_id,
            starts_on=date(2026, 8, 1),
        )
    )
    pause = aggregate.resume(date(2026, 9, 1))
    assert pause.ends_on == date(2026, 8, 31)
    assert not pause.contains(date(2026, 9, 1))


def test_duplicate_active_exception_rejected() -> None:
    rule = RecurringRule(organization_id=uuid4())
    key = OccurrenceKey.for_recurring_rule(rule.id, date(2026, 8, 15)).value
    aggregate = RecurringAggregate(rule=rule, versions=[
        _monthly_version(rule, effective_from=date(2026, 1, 1)),
    ])
    aggregate.add_exception(
        RecurringOccurrenceException(
            organization_id=rule.organization_id,
            recurring_rule_id=rule.id,
            original_occurrence_key=key,
            original_expected_on=date(2026, 8, 15),
            exception_type=RecurringExceptionType.SKIP,
        )
    )
    with pytest.raises(DuplicateOccurrenceException):
        aggregate.add_exception(
            RecurringOccurrenceException(
                organization_id=rule.organization_id,
                recurring_rule_id=rule.id,
                original_occurrence_key=key,
                original_expected_on=date(2026, 8, 15),
                exception_type=RecurringExceptionType.SKIP,
            )
        )
