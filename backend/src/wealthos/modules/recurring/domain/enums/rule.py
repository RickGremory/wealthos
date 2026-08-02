"""Fix StrEnum parse helpers without fragile mixin."""

from __future__ import annotations

from enum import StrEnum

from wealthos.modules.recurring.domain.exceptions import RecurringError


def _parse_strenum[T: StrEnum](enum_cls: type[T], value: str | T, *, label: str) -> T:
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(str(value).strip().lower())
    except ValueError as exc:
        allowed = ", ".join(member.value for member in enum_cls)
        raise RecurringError(
            f"{label} must be one of: {allowed}.",
            code=f"invalid_{label.lower().replace(' ', '_')}",
        ) from exc


class RecurringRuleStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"

    @classmethod
    def parse(cls, value: str | RecurringRuleStatus) -> RecurringRuleStatus:
        return _parse_strenum(cls, value, label="Rule status")


class RecurringSourceType(StrEnum):
    MANUAL = "manual"
    COMMITMENT = "commitment"
    GOAL = "goal"
    TAX = "tax"
    SYSTEM = "system"
    IMPORTED = "imported"

    @classmethod
    def parse(cls, value: str | RecurringSourceType) -> RecurringSourceType:
        return _parse_strenum(cls, value, label="Source type")

    @property
    def is_managed_externally(self) -> bool:
        return self is not RecurringSourceType.MANUAL


class RecurringDirection(StrEnum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"
    TRANSFER = "transfer"

    @classmethod
    def parse(cls, value: str | RecurringDirection) -> RecurringDirection:
        return _parse_strenum(cls, value, label="Direction")


class RecurringAmountStrategy(StrEnum):
    FIXED = "fixed"
    ESTIMATED = "estimated"

    @classmethod
    def parse(cls, value: str | RecurringAmountStrategy) -> RecurringAmountStrategy:
        return _parse_strenum(cls, value, label="Amount strategy")


class RecurringCertainty(StrEnum):
    CONFIRMED = "confirmed"
    EXPECTED = "expected"
    ESTIMATED = "estimated"

    @classmethod
    def parse(cls, value: str | RecurringCertainty) -> RecurringCertainty:
        return _parse_strenum(cls, value, label="Certainty")
