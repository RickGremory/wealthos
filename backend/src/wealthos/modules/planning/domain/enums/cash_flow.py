"""Cash flow direction, certainty and status (SPEC-004 §5)."""

from __future__ import annotations

from enum import StrEnum

from wealthos.modules.planning.domain.exceptions import (
    InvalidCashFlowCertainty,
    InvalidCashFlowDirection,
    InvalidCashFlowStatus,
)


class CashFlowDirection(StrEnum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"

    @classmethod
    def parse(cls, value: str | CashFlowDirection) -> CashFlowDirection:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            raise InvalidCashFlowDirection("Direction must be inflow or outflow.") from exc

    @property
    def is_inflow(self) -> bool:
        return self is CashFlowDirection.INFLOW

    @property
    def is_outflow(self) -> bool:
        return self is CashFlowDirection.OUTFLOW


class CashFlowCertainty(StrEnum):
    CONFIRMED = "confirmed"
    EXPECTED = "expected"
    ESTIMATED = "estimated"

    @classmethod
    def parse(cls, value: str | CashFlowCertainty) -> CashFlowCertainty:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise InvalidCashFlowCertainty(f"Certainty must be one of: {allowed}.") from exc


class CashFlowStatus(StrEnum):
    """Lifecycle of a planned occurrence.

    ``active`` / ``settled`` / ``cancelled`` / ``expired`` are persistable on
    ``planned_cash_flows``; ``partially_settled`` only exists in-flight while
    the engine reconciles settlements.
    """

    ACTIVE = "active"
    PARTIALLY_SETTLED = "partially_settled"
    SETTLED = "settled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    @classmethod
    def parse(cls, value: str | CashFlowStatus) -> CashFlowStatus:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise InvalidCashFlowStatus(f"Status must be one of: {allowed}.") from exc

    @property
    def is_persistable(self) -> bool:
        return self is not CashFlowStatus.PARTIALLY_SETTLED

    @property
    def affects_projection(self) -> bool:
        return self in {CashFlowStatus.ACTIVE, CashFlowStatus.PARTIALLY_SETTLED}


PERSISTABLE_CASH_FLOW_STATUSES = frozenset(
    member.value for member in CashFlowStatus if member.is_persistable
)
