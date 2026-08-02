"""Occurrence status and exception / settlement enums."""

from __future__ import annotations

from enum import StrEnum

from wealthos.modules.recurring.domain.exceptions import RecurringError


class RecurringOccurrenceStatus(StrEnum):
    UPCOMING = "upcoming"
    DUE = "due"
    OVERDUE = "overdue"
    SETTLED = "settled"
    PARTIALLY_SETTLED = "partially_settled"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

    @classmethod
    def parse(cls, value: str | RecurringOccurrenceStatus) -> RecurringOccurrenceStatus:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise RecurringError(
                f"Occurrence status must be one of: {allowed}.",
                code="invalid_occurrence_status",
            ) from exc


class RecurringExceptionType(StrEnum):
    SKIP = "skip"
    RESCHEDULE = "reschedule"
    AMOUNT_OVERRIDE = "amount_override"
    OVERRIDE = "override"

    @classmethod
    def parse(cls, value: str | RecurringExceptionType) -> RecurringExceptionType:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise RecurringError(
                f"Exception type must be one of: {allowed}.",
                code="invalid_occurrence_exception",
            ) from exc


class RecurringSettlementMode(StrEnum):
    SINGLE_TRANSACTION = "single_transaction"
    CUMULATIVE = "cumulative"

    @classmethod
    def parse(cls, value: str | RecurringSettlementMode) -> RecurringSettlementMode:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise RecurringError(
                f"Settlement mode must be one of: {allowed}.",
                code="invalid_settlement_mode",
            ) from exc


class RecurringSettlementLinkType(StrEnum):
    EXPLICIT = "explicit"
    MANUAL = "manual"
    SUGGESTED_CONFIRMED = "suggested_confirmed"

    @classmethod
    def parse(cls, value: str | RecurringSettlementLinkType) -> RecurringSettlementLinkType:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise RecurringError(
                f"Link type must be one of: {allowed}.",
                code="invalid_settlement_link_type",
            ) from exc
