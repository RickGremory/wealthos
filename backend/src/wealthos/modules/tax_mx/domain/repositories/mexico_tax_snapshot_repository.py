"""Persistence port for calculation snapshots."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


class MexicoTaxSnapshotRepository(Protocol):
    def add(
        self,
        *,
        organization_id: UUID,
        tax_calculation_id: UUID,
        configuration_version: int,
        catalog_version: str,
        calculation_engine: str,
        calculation_engine_version: str,
        transaction_cutoff_at: datetime,
        workpaper_json: dict[str, Any],
    ) -> UUID: ...

    def get_by_calculation(
        self, organization_id: UUID, tax_calculation_id: UUID
    ) -> dict[str, Any] | None: ...
