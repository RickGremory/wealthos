"""Parametrized tests for DefaultRecurrenceGenerator."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

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
from wealthos.modules.recurring.domain.enums.occurrence import (
    RecurringExceptionType,
    RecurringOccurrenceStatus,
    RecurringSettlementLinkType,
)
from wealthos.modules.recurring.domain.enums.recurrence import (
    InvalidDatePolicy,
    RecurrenceFrequency,
    Weekday,
)
from wealthos.modules.recurring.domain.enums.rule import RecurringDirection
from wealthos.modules.recurring.domain.services.recurrence_generator import (
    DefaultRecurrenceGenerator,
)
from wealthos.modules.recurring.domain.value_objects.occurrence_key import OccurrenceKey
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


def _rule_version(
    *,
    frequency: RecurrenceFrequency,
    interval: int = 1,
    starts_on: date,
    day_of_month: int | None = None,
    end_of_month: bool = False,
    days_of_week: tuple[Weekday, ...] = (),
    month_of_year: int | None = None,
    invalid_date_policy: InvalidDatePolicy = InvalidDatePolicy.LAST_DAY_OF_MONTH,
    amount: str = "800.00",
) -> tuple[RecurringRule, RecurringRuleVersion]:
    rule = RecurringRule(organization_id=uuid4())
    pattern = RecurrencePattern(
        frequency=frequency,
        interval=interval,
        day_of_month=day_of_month,
        end_of_month=end_of_month,
        days_of_week=days_of_week,
        month_of_year=month_of_year,
        invalid_date_policy=invalid_date_policy,
    )
    version = RecurringRuleVersion(
        recurring_rule_id=rule.id,
        organization_id=rule.organization_id,
        effective_from=starts_on,
        name="Test",
        direction=RecurringDirection.OUTFLOW,
        amount=Decimal(amount),
        currency="MXN",
        pattern=pattern,
        starts_on=starts_on,
    )
    return rule, version


@pytest.mark.parametrize(
    ("starts_on", "interval", "period_start", "period_end", "expected"),
    [
        (
            date(2026, 8, 1),
            1,
            date(2026, 8, 1),
            date(2026, 8, 3),
            [date(2026, 8, 1), date(2026, 8, 2), date(2026, 8, 3)],
        ),
        (
            date(2026, 8, 1),
            5,
            date(2026, 8, 8),
            date(2026, 8, 25),
            [date(2026, 8, 11), date(2026, 8, 16), date(2026, 8, 21)],
        ),
    ],
)
def test_daily_generation(starts_on, interval, period_start, period_end, expected) -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.DAILY,
        interval=interval,
        starts_on=starts_on,
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=period_start,
        period_end=period_end,
        evaluated_on=date(2026, 8, 1),
        timezone="America/Merida",
    )
    assert [item.expected_on for item in result] == expected


def test_monthly_day_15() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.MONTHLY,
        starts_on=date(2026, 7, 15),
        day_of_month=15,
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 10, 31),
        evaluated_on=date(2026, 8, 1),
        timezone="America/Merida",
    )
    assert [item.expected_on for item in result] == [
        date(2026, 8, 15),
        date(2026, 9, 15),
        date(2026, 10, 15),
    ]


def test_monthly_day_31_last_day_policy() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.MONTHLY,
        starts_on=date(2026, 1, 31),
        day_of_month=31,
        invalid_date_policy=InvalidDatePolicy.LAST_DAY_OF_MONTH,
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 4, 30),
        evaluated_on=date(2026, 1, 1),
        timezone="America/Merida",
    )
    assert [item.expected_on for item in result] == [
        date(2026, 1, 31),
        date(2026, 2, 28),
        date(2026, 3, 31),
        date(2026, 4, 30),
    ]


def test_weekly_biweekly_friday() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.WEEKLY,
        interval=2,
        starts_on=date(2026, 8, 7),
        days_of_week=(Weekday.FRIDAY,),
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 9, 30),
        evaluated_on=date(2026, 8, 1),
        timezone="America/Merida",
    )
    assert [item.expected_on for item in result] == [
        date(2026, 8, 7),
        date(2026, 8, 21),
        date(2026, 9, 4),
        date(2026, 9, 18),
    ]


def test_pause_excludes_base_date() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.MONTHLY,
        starts_on=date(2026, 7, 15),
        day_of_month=15,
    )
    pause = RecurringRulePause(
        recurring_rule_id=rule.id,
        organization_id=rule.organization_id,
        starts_on=date(2026, 8, 1),
        ends_on=date(2026, 8, 31),
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 9, 30),
        pauses=(pause,),
        evaluated_on=date(2026, 8, 1),
        timezone="America/Merida",
    )
    assert [item.expected_on for item in result] == [date(2026, 9, 15)]


def test_reschedule_keeps_original_key() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.MONTHLY,
        starts_on=date(2026, 7, 15),
        day_of_month=15,
    )
    original = date(2026, 8, 15)
    key = OccurrenceKey.for_recurring_rule(rule.id, original)
    exception = RecurringOccurrenceException(
        organization_id=rule.organization_id,
        recurring_rule_id=rule.id,
        original_occurrence_key=key.value,
        original_expected_on=original,
        exception_type=RecurringExceptionType.RESCHEDULE,
        replacement_expected_on=date(2026, 8, 17),
        replacement_amount=Decimal("850.00"),
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 8, 31),
        exceptions=(exception,),
        evaluated_on=date(2026, 8, 1),
        timezone="America/Merida",
    )
    assert len(result) == 1
    assert result[0].expected_on == date(2026, 8, 17)
    assert result[0].original_expected_on == original
    assert result[0].occurrence_key.value == key.value
    assert result[0].expected_amount == Decimal("850.00")


def test_settlement_marks_settled() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.MONTHLY,
        starts_on=date(2026, 7, 15),
        day_of_month=15,
    )
    original = date(2026, 8, 15)
    key = OccurrenceKey.for_recurring_rule(rule.id, original)
    settlement = RecurringOccurrenceSettlement(
        organization_id=rule.organization_id,
        recurring_rule_id=rule.id,
        occurrence_key=key.value,
        transaction_id=uuid4(),
        settled_amount=Decimal("817.00"),
        link_type=RecurringSettlementLinkType.EXPLICIT,
    )
    result = DefaultRecurrenceGenerator().generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 8, 31),
        settlements=(settlement,),
        evaluated_on=date(2026, 8, 20),
        timezone="America/Merida",
    )
    assert result[0].status is RecurringOccurrenceStatus.SETTLED
    assert result[0].variance_amount == Decimal("17.00")


def test_status_due_and_overdue() -> None:
    rule, version = _rule_version(
        frequency=RecurrenceFrequency.MONTHLY,
        starts_on=date(2026, 7, 15),
        day_of_month=15,
    )
    gen = DefaultRecurrenceGenerator()
    due = gen.generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 8, 31),
        evaluated_on=date(2026, 8, 15),
        timezone="America/Merida",
    )
    overdue = gen.generate(
        rule=rule,
        version=version,
        period_start=date(2026, 8, 1),
        period_end=date(2026, 8, 31),
        evaluated_on=date(2026, 8, 16),
        timezone="America/Merida",
    )
    assert due[0].status is RecurringOccurrenceStatus.DUE
    assert overdue[0].status is RecurringOccurrenceStatus.OVERDUE
