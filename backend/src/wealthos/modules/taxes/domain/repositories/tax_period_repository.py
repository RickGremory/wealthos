"""Persistence port for TaxPeriod aggregates."""

from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_period import TaxPeriod


class TaxPeriodRepository(Protocol):
    def add(self, period: TaxPeriod) -> TaxPeriod: ...

    def get_by_id(
        self,
        organization_id: UUID,
        period_id: UUID,
    ) -> TaxPeriod | None: ...

    def get_by_range(
        self,
        tax_profile_id: UUID,
        date_from: date,
        date_to: date,
    ) -> TaxPeriod | None: ...

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
    ) -> list[TaxPeriod]: ...

    def lock_for_update(
        self,
        organization_id: UUID,
        period_id: UUID,
    ) -> TaxPeriod | None: ...

    def save(self, period: TaxPeriod) -> TaxPeriod: ...
