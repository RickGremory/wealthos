"""Recurring domain exceptions (SPEC-005)."""

from __future__ import annotations


class RecurringError(Exception):
    """Base recurring domain error."""

    code: str = "recurring_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class InvalidRecurrencePattern(RecurringError):
    code = "invalid_recurrence_pattern"


class RecurringVersionOverlap(RecurringError):
    code = "recurring_version_overlap"


class InvalidEffectiveDate(RecurringError):
    code = "invalid_effective_date"


class PauseAlreadyOpen(RecurringError):
    code = "pause_already_open"


class PauseNotOpen(RecurringError):
    code = "pause_not_open"


class PausePeriodOverlap(RecurringError):
    code = "pause_period_overlap"


class RecurringConcurrentUpdate(RecurringError):
    code = "concurrent_update"


class RecurringRuleArchived(RecurringError):
    code = "recurring_rule_archived"


class DuplicateOccurrenceException(RecurringError):
    code = "duplicate_occurrence_exception"


class InvalidOccurrenceException(RecurringError):
    code = "invalid_occurrence_exception"


class InvalidPausePeriod(RecurringError):
    code = "invalid_pause_period"


class InvalidRecurrenceRange(RecurringError):
    code = "invalid_recurrence_range"


class RecurrenceRangeTooLarge(RecurringError):
    code = "recurrence_range_too_large"


class RecurrenceOccurrenceLimitExceeded(RecurringError):
    code = "occurrence_limit_exceeded"


class UnsupportedRecurrenceFrequency(RecurringError):
    code = "unsupported_recurrence_frequency"


class UnsupportedInvalidDatePolicy(RecurringError):
    code = "unsupported_invalid_date_policy"
