"""Resolve a horizon into a concrete window in the org timezone (§4)."""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from zoneinfo import ZoneInfo

from wealthos.modules.planning.domain.enums.planning_horizon import PlanningHorizon
from wealthos.modules.planning.domain.value_objects.projection_result import ProjectionPeriod

DEFAULT_TIMEZONE = "UTC"


class PlanningHorizonResolver:
    """"Today" is the user's local day, never naive UTC."""

    def resolve(
        self,
        *,
        horizon: str | PlanningHorizon,
        timezone: str = DEFAULT_TIMEZONE,
        calculated_at: datetime,
    ) -> ProjectionPeriod:
        parsed = PlanningHorizon.parse(horizon)
        zone = ZoneInfo(timezone)
        moment = calculated_at if calculated_at.tzinfo is not None else calculated_at.replace(tzinfo=UTC)
        local_now = moment.astimezone(zone)

        start_date = local_now.date()
        end_date = start_date + timedelta(days=parsed.days)

        start = datetime.combine(start_date, time.min, tzinfo=zone)
        end = datetime.combine(end_date, time.max, tzinfo=zone)

        return ProjectionPeriod(
            horizon=parsed,
            start=start,
            end=end,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
        )
