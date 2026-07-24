"""Expand cash-plan recurrence rules within a bounded date window."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

_MAX_OCCURRENCES = 500
_MAX_WALK_STEPS = 20_000


class CashPlanOccurrenceGenerator:
    """Pure RRULE expander (no DB). Supports DAILY / WEEKLY / MONTHLY / YEARLY."""

    def expand(
        self,
        *,
        expected_date: date,
        recurrence_rule: str | None,
        date_from: date,
        date_to: date,
        max_occurrences: int = _MAX_OCCURRENCES,
    ) -> tuple[date, ...]:
        if date_to < date_from:
            return ()

        if not recurrence_rule or not recurrence_rule.strip():
            if date_from <= expected_date <= date_to:
                return (expected_date,)
            return ()

        params = _parse_rrule(recurrence_rule)
        freq = params.get("FREQ")
        if freq is None:
            if date_from <= expected_date <= date_to:
                return (expected_date,)
            return ()

        interval = max(int(params.get("INTERVAL", "1")), 1)
        count = int(params["COUNT"]) if "COUNT" in params else None
        until = _parse_until(params.get("UNTIL"))
        hard_end = date_to if until is None else min(date_to, until)

        bymonthday = int(params["BYMONTHDAY"]) if "BYMONTHDAY" in params else expected_date.day

        occurrences: list[date] = []
        cursor = expected_date
        emitted_from_start = 0
        steps = 0

        while steps < _MAX_WALK_STEPS and cursor <= hard_end:
            steps += 1
            if count is not None and emitted_from_start >= count:
                break

            if cursor >= date_from:
                occurrences.append(cursor)
                if len(occurrences) >= max_occurrences:
                    break

            emitted_from_start += 1
            nxt = _next_occurrence(
                cursor,
                freq=freq,
                interval=interval,
                bymonthday=bymonthday,
            )
            if nxt is None or nxt <= cursor:
                break
            cursor = nxt

        return tuple(occurrences)


def _parse_rrule(raw: str) -> dict[str, str]:
    text = raw.strip()
    if text.upper().startswith("RRULE:"):
        text = text[6:]
    params: dict[str, str] = {}
    for part in text.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        params[key.strip().upper()] = value.strip()
    return params


def _parse_until(raw: str | None) -> date | None:
    if not raw:
        return None
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) < 8:
        return None
    return date(int(digits[0:4]), int(digits[4:6]), int(digits[6:8]))


def _next_occurrence(
    current: date,
    *,
    freq: str,
    interval: int,
    bymonthday: int,
) -> date | None:
    freq = freq.upper()
    if freq == "DAILY":
        return current + timedelta(days=interval)
    if freq == "WEEKLY":
        return current + timedelta(weeks=interval)
    if freq == "MONTHLY":
        return _add_months(current, interval, bymonthday=bymonthday)
    if freq == "YEARLY":
        return _add_months(current, interval * 12, bymonthday=bymonthday)
    return None


def _add_months(current: date, months: int, *, bymonthday: int) -> date:
    month_index = current.year * 12 + (current.month - 1) + months
    year, month0 = divmod(month_index, 12)
    month = month0 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(bymonthday, last_day)
    return date(year, month, day)
