"""Map domain objects to query DTOs."""

from __future__ import annotations

from wealthos.modules.recurring.application.dto.views import (
    RecurringOccurrenceDTO,
    RecurringVersionDTO,
)
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.occurrence import RecurringOccurrenceStatus
from wealthos.modules.recurring.domain.value_objects.recurring_occurrence import (
    RecurringOccurrence,
)


def schedule_label(version: RecurringRuleVersion) -> str:
    pattern = version.pattern
    freq = pattern.frequency.value
    if pattern.interval == 1:
        base = {
            "daily": "Diario",
            "weekly": "Semanal",
            "monthly": "Mensual",
            "yearly": "Anual",
        }.get(freq, freq)
    else:
        base = f"Cada {pattern.interval} ({freq})"
    if pattern.day_of_month:
        return f"{base} · día {pattern.day_of_month}"
    if pattern.end_of_month:
        return f"{base} · último día"
    if pattern.days_of_week:
        days = ",".join(str(int(day)) for day in pattern.days_of_week)
        return f"{base} · días {days}"
    return base


def version_to_dto(version: RecurringRuleVersion) -> RecurringVersionDTO:
    pattern = version.pattern
    return RecurringVersionDTO(
        id=version.id,
        effective_from=version.effective_from,
        effective_until=version.effective_until,
        name=version.name,
        direction=version.direction.value,
        amount=str(version.amount),
        currency=version.currency,
        frequency=pattern.frequency.value,
        interval=pattern.interval,
        day_of_month=pattern.day_of_month,
        end_of_month=pattern.end_of_month,
        days_of_week=tuple(int(day) for day in pattern.days_of_week),
        month_of_year=pattern.month_of_year,
        invalid_date_policy=pattern.invalid_date_policy.value,
        starts_on=version.starts_on,
        ends_on=version.ends_on,
        grace_period_days=version.grace_period_days,
        amount_strategy=version.amount_strategy.value,
        certainty=version.certainty.value,
        settlement_mode=version.settlement_mode.value,
        account_id=version.account_id,
        destination_account_id=version.destination_account_id,
        category_id=version.category_id,
        notes=version.notes,
    )


def occurrence_to_dto(
    occurrence: RecurringOccurrence,
    *,
    name: str,
    exception_type: str | None = None,
) -> RecurringOccurrenceDTO:
    settled_like = occurrence.status in {
        RecurringOccurrenceStatus.SETTLED,
        RecurringOccurrenceStatus.SKIPPED,
        RecurringOccurrenceStatus.CANCELLED,
    }
    return RecurringOccurrenceDTO(
        occurrence_key=occurrence.occurrence_key.value,
        recurring_rule_id=occurrence.recurring_rule_id,
        original_expected_on=occurrence.original_expected_on,
        expected_on=occurrence.expected_on,
        expected_at=occurrence.expected_at,
        direction=occurrence.direction.value,
        base_amount=str(occurrence.base_amount),
        expected_amount=str(occurrence.expected_amount),
        currency=occurrence.currency,
        certainty=occurrence.certainty.value,
        status=occurrence.status.value,
        is_exception=occurrence.is_exception,
        exception_type=exception_type,
        name=name,
        account_id=occurrence.account_id,
        destination_account_id=occurrence.destination_account_id,
        category_id=occurrence.category_id,
        actual_amount=(
            str(occurrence.actual_amount) if occurrence.actual_amount is not None else None
        ),
        variance_amount=(
            str(occurrence.variance_amount)
            if occurrence.variance_amount is not None
            else None
        ),
        can_confirm=not settled_like,
        can_skip=not settled_like,
        can_reschedule=not settled_like,
    )
