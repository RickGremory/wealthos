"""Persistence port for Mexico withholdings."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_withholding import (
    MexicoTaxWithholding,
)


class MexicoTaxWithholdingRepository(Protocol):
    def add(self, withholding: MexicoTaxWithholding) -> MexicoTaxWithholding: ...

    def list_by_transactions(
        self, organization_id: UUID, transaction_ids: list[UUID]
    ) -> list[MexicoTaxWithholding]: ...
