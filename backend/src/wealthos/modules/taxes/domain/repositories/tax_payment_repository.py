"""Persistence port for TaxPayment records."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_payment import TaxPayment


class TaxPaymentRepository(Protocol):
    def add(self, payment: TaxPayment) -> TaxPayment: ...

    def get_by_idempotency_key(
        self,
        organization_id: UUID,
        idempotency_key: str,
    ) -> TaxPayment | None: ...

    def list_by_period(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
    ) -> list[TaxPayment]: ...

    def sum_by_period(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
        *,
        currency: str | None = None,
    ) -> Decimal: ...
