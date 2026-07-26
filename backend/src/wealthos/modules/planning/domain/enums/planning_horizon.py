"""Planning horizons — today / 7 / 30 / 90 days (SPEC-004 §5)."""

from __future__ import annotations

from enum import StrEnum

from wealthos.modules.planning.domain.exceptions import InvalidPlanningHorizon


class PlanningHorizon(StrEnum):
    TODAY = "today"
    SEVEN_DAYS = "7_days"
    THIRTY_DAYS = "30_days"
    NINETY_DAYS = "90_days"

    @property
    def days(self) -> int:
        """Calendar days added to ``period_start``. `30_days` is not end-of-month."""
        return _DAYS[self]

    @classmethod
    def parse(cls, value: str | PlanningHorizon) -> PlanningHorizon:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise InvalidPlanningHorizon(f"Horizon must be one of: {allowed}.") from exc


_DAYS: dict[PlanningHorizon, int] = {
    PlanningHorizon.TODAY: 0,
    PlanningHorizon.SEVEN_DAYS: 7,
    PlanningHorizon.THIRTY_DAYS: 30,
    PlanningHorizon.NINETY_DAYS: 90,
}
