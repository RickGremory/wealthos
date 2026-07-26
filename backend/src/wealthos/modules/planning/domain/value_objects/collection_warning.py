"""Adapter-level warnings and freshness metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from wealthos.modules.planning.domain.enums.alert import AlertSeverity
from wealthos.modules.planning.domain.enums.source import SourceStatus


@dataclass(frozen=True, slots=True)
class PlanningCollectionWarning:
    """"No data" and "could not fetch" are different — say which."""

    code: str
    source_name: str
    message_key: str
    severity: AlertSeverity = AlertSeverity.WARNING
    related_resource_type: str | None = None
    related_resource_id: str | None = None


@dataclass(frozen=True, slots=True)
class PlanningSourceMetadata:
    source_name: str
    collected_at: datetime
    data_as_of: datetime | None
    status: SourceStatus
