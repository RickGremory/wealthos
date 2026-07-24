"""TaxPayment — links a fiscal payment to an expense transaction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.exceptions import TaxPaymentAmountInvalid
from wealthos.modules.taxes.domain.value_objects.tax_type import TaxType
from wealthos.shared.domain.value_objects.money import Money


@dataclass(slots=True)
class TaxPayment:
    id: UUID
    organization_id: UUID
    tax_period_id: UUID
    tax_type: TaxType
    transaction_id: UUID
    source_account_id: UUID
    amount: Money
    paid_at: datetime
    reference: str | None
    notes: str | None
    idempotency_key: str | None
    created_by_user_id: UUID
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_period_id: UUID,
        tax_type: str,
        transaction_id: UUID,
        source_account_id: UUID,
        amount: Money,
        paid_at: datetime,
        created_by_user_id: UUID,
        reference: str | None = None,
        notes: str | None = None,
        idempotency_key: str | None = None,
        payment_id: UUID | None = None,
    ) -> TaxPayment:
        if amount.amount <= Decimal("0.00"):
            raise TaxPaymentAmountInvalid("Tax payment amount must be positive.")
        return cls(
            id=payment_id or uuid4(),
            organization_id=organization_id,
            tax_period_id=tax_period_id,
            tax_type=TaxType(tax_type),
            transaction_id=transaction_id,
            source_account_id=source_account_id,
            amount=amount,
            paid_at=paid_at,
            reference=reference.strip() if reference else None,
            notes=notes.strip() if notes else None,
            idempotency_key=idempotency_key,
            created_by_user_id=created_by_user_id,
            created_at=datetime.now(UTC),
        )
