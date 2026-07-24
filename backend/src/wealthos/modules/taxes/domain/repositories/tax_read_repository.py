"""Read-only tax queries over transactions and accounts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.application.services.tax_calculation_service import (
    TaxPaymentView,
    TaxTransactionView,
)


class TaxReadRepository(Protocol):
    def get_taxable_transactions(
        self,
        organization_id: UUID,
        *,
        date_from: date,
        date_to: date,
    ) -> list[TaxTransactionView]: ...

    def get_period_payments(
        self,
        organization_id: UUID,
        tax_period_id: UUID,
    ) -> list[TaxPaymentView]: ...

    def get_reserve_account_balance(
        self,
        organization_id: UUID,
        account_id: UUID,
    ) -> Decimal | None: ...
