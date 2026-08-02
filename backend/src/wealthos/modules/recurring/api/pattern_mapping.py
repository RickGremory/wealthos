"""Convert API pattern schemas to domain RecurrencePattern."""

from __future__ import annotations

from wealthos.modules.recurring.api.schemas import (
    DailyPatternSchema,
    MonthlyPatternSchema,
    RecurrencePatternSchema,
    WeeklyPatternSchema,
    YearlyPatternSchema,
)
from wealthos.modules.recurring.domain.enums.recurrence import (
    InvalidDatePolicy,
    RecurrenceFrequency,
    Weekday,
)
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)


def pattern_from_schema(schema: RecurrencePatternSchema) -> RecurrencePattern:
    if isinstance(schema, DailyPatternSchema):
        return RecurrencePattern(
            frequency=RecurrenceFrequency.DAILY,
            interval=schema.interval,
        )
    if isinstance(schema, WeeklyPatternSchema):
        return RecurrencePattern(
            frequency=RecurrenceFrequency.WEEKLY,
            interval=schema.interval,
            days_of_week=tuple(Weekday.parse(day) for day in schema.days_of_week),
        )
    if isinstance(schema, MonthlyPatternSchema):
        return RecurrencePattern(
            frequency=RecurrenceFrequency.MONTHLY,
            interval=schema.interval,
            day_of_month=schema.day_of_month,
            end_of_month=schema.end_of_month,
            invalid_date_policy=InvalidDatePolicy.parse(schema.invalid_date_policy),
        )
    if isinstance(schema, YearlyPatternSchema):
        return RecurrencePattern(
            frequency=RecurrenceFrequency.YEARLY,
            interval=schema.interval,
            month_of_year=schema.month_of_year,
            day_of_month=schema.day_of_month,
            end_of_month=schema.end_of_month,
            invalid_date_policy=InvalidDatePolicy.parse(schema.invalid_date_policy),
        )
    raise TypeError(f"Unsupported pattern schema: {type(schema)}")
