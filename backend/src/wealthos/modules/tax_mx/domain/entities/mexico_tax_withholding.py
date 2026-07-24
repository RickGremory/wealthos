"""Mexico tax withholding entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.tax_mx.domain.exceptions import InvalidMexicoTaxConfiguration
from wealthos.modules.tax_mx.domain.value_objects.estimation import MexicoWithholdingType
from wealthos.modules.tax_mx.domain.value_objects.rfc import RFC
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class MexicoTaxWithholding:
    id: UUID
    organization_id: UUID
    transaction_id: UUID
    withholding_type: MexicoWithholdingType
    base_amount: Money
    rate: Percentage | None
    amount: Money
    withheld_by_rfc: RFC | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        transaction_id: UUID,
        withholding_type: str,
        base_amount: Money,
        amount: Money,
        rate: Decimal | None = None,
        withheld_by_rfc: str | None = None,
        withholding_id: UUID | None = None,
    ) -> MexicoTaxWithholding:
        if amount.amount < 0:
            raise InvalidMexicoTaxConfiguration("Withholding amount cannot be negative.")
        if base_amount.currency != amount.currency:
            raise InvalidMexicoTaxConfiguration("Withholding currencies must match.")
        now = datetime.now(UTC)
        return cls(
            id=withholding_id or uuid4(),
            organization_id=organization_id,
            transaction_id=transaction_id,
            withholding_type=MexicoWithholdingType(withholding_type),
            base_amount=base_amount,
            rate=Percentage(rate) if rate is not None else None,
            amount=amount,
            withheld_by_rfc=RFC(withheld_by_rfc) if withheld_by_rfc else None,
            created_at=now,
            updated_at=now,
        )
