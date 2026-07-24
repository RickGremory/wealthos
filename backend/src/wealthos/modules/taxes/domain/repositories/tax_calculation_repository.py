"""Persistence port for TaxCalculation snapshots."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_calculation import TaxCalculation


class TaxCalculationRepository(Protocol):
    def add(self, calculation: TaxCalculation) -> TaxCalculation: ...

    def get_by_id(
        self,
        organization_id: UUID,
        calculation_id: UUID,
    ) -> TaxCalculation | None: ...

    def get_latest_by_period(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
    ) -> TaxCalculation | None: ...

    def get_next_version(self, tax_period_id: UUID) -> int: ...

    def supersede_completed(self, tax_period_id: UUID) -> None: ...
