"""Foreign-exchange transfer aggregate (Sprint 9.6)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from wealthos.modules.transactions.domain.exceptions import (
    InvalidTransactionEntries,
    SameAccountTransfer,
)


RATE_QUANT = Decimal("0.0000000001")
MONEY_QUANT = Decimal("0.01")


def derive_effective_rate(source_amount: Decimal, destination_amount: Decimal) -> Decimal:
    if source_amount <= 0 or destination_amount <= 0:
        raise InvalidTransactionEntries("FX amounts must be positive.")
    return (source_amount / destination_amount).quantize(RATE_QUANT, rounding=ROUND_HALF_UP)


@dataclass(slots=True)
class FxTransfer:
    id: UUID
    organization_id: UUID
    source_account_id: UUID
    destination_account_id: UUID
    source_amount: Decimal
    source_currency: str
    destination_amount: Decimal
    destination_currency: str
    effective_exchange_rate: Decimal
    fee_amount: Decimal | None
    fee_currency: str | None
    occurred_at: datetime
    description: str
    notes: str | None
    source_transaction_id: UUID
    destination_transaction_id: UUID
    fee_transaction_id: UUID | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        source_account_id: UUID,
        destination_account_id: UUID,
        source_amount: Decimal,
        source_currency: str,
        destination_amount: Decimal,
        destination_currency: str,
        occurred_at: datetime,
        description: str,
        created_by_user_id: UUID,
        source_transaction_id: UUID,
        destination_transaction_id: UUID,
        fee_amount: Decimal | None = None,
        fee_currency: str | None = None,
        fee_transaction_id: UUID | None = None,
        notes: str | None = None,
        fx_id: UUID | None = None,
    ) -> FxTransfer:
        if source_account_id == destination_account_id:
            raise SameAccountTransfer("FX accounts must be different.")
        src_ccy = source_currency.strip().upper()
        dst_ccy = destination_currency.strip().upper()
        if src_ccy == dst_ccy:
            raise InvalidTransactionEntries(
                "FX conversion requires different currencies."
            )
        src = Decimal(source_amount).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
        dst = Decimal(destination_amount).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
        rate = derive_effective_rate(src, dst)
        fee = None
        fee_ccy = None
        if fee_amount is not None:
            fee = Decimal(fee_amount).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
            if fee <= 0:
                raise InvalidTransactionEntries("FX fee must be positive when provided.")
            fee_ccy = (fee_currency or src_ccy).strip().upper()
        now = datetime.now(UTC)
        return cls(
            id=fx_id or uuid4(),
            organization_id=organization_id,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            source_amount=src,
            source_currency=src_ccy,
            destination_amount=dst,
            destination_currency=dst_ccy,
            effective_exchange_rate=rate,
            fee_amount=fee,
            fee_currency=fee_ccy,
            occurred_at=occurred_at,
            description=description.strip(),
            notes=notes.strip() if notes and notes.strip() else None,
            source_transaction_id=source_transaction_id,
            destination_transaction_id=destination_transaction_id,
            fee_transaction_id=fee_transaction_id,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
