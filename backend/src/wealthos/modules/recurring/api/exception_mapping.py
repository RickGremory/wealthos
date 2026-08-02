"""Map Recurring domain errors to HTTP responses."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from fastapi import HTTPException, status

from wealthos.modules.recurring.domain.exceptions import (
    DuplicateOccurrenceException,
    InvalidOccurrenceException,
    InvalidPausePeriod,
    InvalidRecurrencePattern,
    InvalidRecurrenceRange,
    OccurrenceAlreadySettled,
    OccurrenceAlreadySkipped,
    OccurrenceNotFound,
    PauseAlreadyOpen,
    PauseNotOpen,
    PausePeriodOverlap,
    RecurrenceOccurrenceLimitExceeded,
    RecurrenceRangeTooLarge,
    RecurringConcurrentUpdate,
    RecurringError,
    RecurringRuleArchived,
    RecurringRuleEnded,
    RecurringRuleManagedExternally,
    RecurringRuleNotFound,
    RecurringVersionOverlap,
    RetroactiveStructuralChangeNotAllowed,
    TransactionAlreadyLinked,
    TransactionNotFound,
)

_STATUS: dict[type[RecurringError], int] = {
    RecurringRuleNotFound: status.HTTP_404_NOT_FOUND,
    OccurrenceNotFound: status.HTTP_404_NOT_FOUND,
    TransactionNotFound: status.HTTP_404_NOT_FOUND,
    RecurringConcurrentUpdate: status.HTTP_409_CONFLICT,
    TransactionAlreadyLinked: status.HTTP_409_CONFLICT,
    DuplicateOccurrenceException: status.HTTP_409_CONFLICT,
    PauseAlreadyOpen: status.HTTP_409_CONFLICT,
    RecurringVersionOverlap: status.HTTP_409_CONFLICT,
    RecurringRuleManagedExternally: status.HTTP_403_FORBIDDEN,
    RecurringRuleArchived: status.HTTP_409_CONFLICT,
    RecurringRuleEnded: status.HTTP_409_CONFLICT,
    RetroactiveStructuralChangeNotAllowed: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidRecurrencePattern: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidRecurrenceRange: status.HTTP_422_UNPROCESSABLE_ENTITY,
    RecurrenceRangeTooLarge: status.HTTP_422_UNPROCESSABLE_ENTITY,
    RecurrenceOccurrenceLimitExceeded: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidOccurrenceException: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidPausePeriod: status.HTTP_422_UNPROCESSABLE_ENTITY,
    PauseNotOpen: status.HTTP_409_CONFLICT,
    PausePeriodOverlap: status.HTTP_409_CONFLICT,
    OccurrenceAlreadySettled: status.HTTP_409_CONFLICT,
    OccurrenceAlreadySkipped: status.HTTP_409_CONFLICT,
}


@contextmanager
def http_map_recurring_errors() -> Iterator[None]:
    try:
        yield
    except RecurringError as exc:
        code = _STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
        raise HTTPException(
            status_code=code,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
