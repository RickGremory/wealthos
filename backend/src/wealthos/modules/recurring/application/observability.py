"""Structured audit + metric logs for Recurring (no PII / amounts / names)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from wealthos.core.logging import get_logger

_log = get_logger("wealthos.recurring.audit")
_metrics = get_logger("wealthos.recurring.metrics")


def audit_recurring(
    action: str,
    *,
    organization_id: UUID,
    actor_id: UUID,
    rule_id: UUID | None = None,
    **fields: Any,
) -> None:
    """Emit `audit.recurring.*` with actor/org/rule ids and safe field diffs."""
    payload: dict[str, Any] = {
        "organization_id": str(organization_id),
        "actor_id": str(actor_id),
        "resource_type": "recurring_rule",
        "action": action,
    }
    if rule_id is not None:
        payload["resource_id"] = str(rule_id)
        payload["rule_id"] = str(rule_id)
    for key, value in fields.items():
        if value is None:
            continue
        payload[key] = str(value) if isinstance(value, UUID) else value
    _log.info(f"audit.recurring.{action}", **payload)


def metric_recurring(event: str, **fields: Any) -> None:
    """Emit counter-like structured metrics without sensitive payloads."""
    safe = {
        key: (str(value) if isinstance(value, UUID) else value)
        for key, value in fields.items()
        if value is not None
    }
    _metrics.info(event, **safe)
