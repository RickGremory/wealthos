"""Dashboard period query parameters."""

from __future__ import annotations

from datetime import date
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, model_validator


class DashboardPeriodParams(BaseModel):
    """Exactly one of: named period, or custom with date_from/date_to."""

    model_config = ConfigDict(extra="forbid")

    period: Literal["this_month", "last_month", "last_30_days", "this_year", "custom"] = (
        "this_month"
    )
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_modality(self) -> Self:
        has_dates = self.date_from is not None or self.date_to is not None
        if self.period != "custom" and has_dates:
            raise ValueError(
                "Do not combine named period with date_from/date_to; use period=custom."
            )
        if self.period == "custom":
            if self.date_from is None or self.date_to is None:
                raise ValueError("custom period requires both date_from and date_to.")
            if self.date_from > self.date_to:
                raise ValueError("date_from must be on or before date_to.")
        return self
