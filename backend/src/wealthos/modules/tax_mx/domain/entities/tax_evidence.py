"""Tax evidence and transaction tax detail entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.tax_mx.domain.exceptions import InvalidTaxDetails
from wealthos.modules.tax_mx.domain.value_objects.estimation import (
    TaxDetailCalculationSource,
)
from wealthos.modules.tax_mx.domain.value_objects.evidence_status import (
    EvidenceSource,
    EvidenceValidationStatus,
    TaxEvidenceType,
)
from wealthos.shared.domain.value_objects.money import Money

_TOLERANCE = Decimal("0.02")
_ZERO = Decimal("0.00")


@dataclass(slots=True)
class TaxEvidence:
    id: UUID
    organization_id: UUID
    transaction_id: UUID
    evidence_type: TaxEvidenceType
    external_reference: str | None
    issuer_rfc: str | None
    receiver_rfc: str | None
    document_date: datetime | None
    subtotal: Money | None
    tax_amount: Money | None
    total: Money | None
    validation_status: EvidenceValidationStatus
    source: EvidenceSource
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        transaction_id: UUID,
        evidence_type: str,
        source: str = "manual",
        validation_status: str = "pending",
        external_reference: str | None = None,
        issuer_rfc: str | None = None,
        receiver_rfc: str | None = None,
        document_date: datetime | None = None,
        subtotal: Money | None = None,
        tax_amount: Money | None = None,
        total: Money | None = None,
        evidence_id: UUID | None = None,
    ) -> TaxEvidence:
        now = datetime.now(UTC)
        return cls(
            id=evidence_id or uuid4(),
            organization_id=organization_id,
            transaction_id=transaction_id,
            evidence_type=TaxEvidenceType(evidence_type),
            external_reference=external_reference.strip() if external_reference else None,
            issuer_rfc=issuer_rfc.strip().upper() if issuer_rfc else None,
            receiver_rfc=receiver_rfc.strip().upper() if receiver_rfc else None,
            document_date=document_date,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total,
            validation_status=EvidenceValidationStatus(validation_status),
            source=EvidenceSource(source),
            created_at=now,
            updated_at=now,
        )

    def mark_valid(self) -> None:
        self.validation_status = EvidenceValidationStatus("valid")
        self.updated_at = datetime.now(UTC)

    def mark_mismatch(self) -> None:
        self.validation_status = EvidenceValidationStatus("mismatch")
        self.updated_at = datetime.now(UTC)

    def mark_invalid(self) -> None:
        self.validation_status = EvidenceValidationStatus("invalid")
        self.updated_at = datetime.now(UTC)


@dataclass(slots=True)
class MexicoTransactionTaxDetails:
    id: UUID
    organization_id: UUID
    transaction_id: UUID
    subtotal: Money
    vat_amount: Money
    withheld_income_tax: Money
    withheld_vat: Money
    other_taxes: Money
    total: Money
    calculation_source: TaxDetailCalculationSource
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        transaction_id: UUID,
        subtotal: Money,
        vat_amount: Money,
        total: Money,
        withheld_income_tax: Money | None = None,
        withheld_vat: Money | None = None,
        other_taxes: Money | None = None,
        calculation_source: str = "manual",
        details_id: UUID | None = None,
    ) -> MexicoTransactionTaxDetails:
        currency = total.currency.value
        wit = withheld_income_tax or Money(_ZERO, currency)
        wvat = withheld_vat or Money(_ZERO, currency)
        other = other_taxes or Money(_ZERO, currency)
        for money in (subtotal, vat_amount, wit, wvat, other):
            if money.currency.value != currency:
                raise InvalidTaxDetails("All tax detail amounts must share currency.")
        expected = subtotal.amount + vat_amount.amount + other.amount - wit.amount - wvat.amount
        if abs(expected - total.amount) > _TOLERANCE:
            raise InvalidTaxDetails("Tax details do not reconcile with total within tolerance.")
        now = datetime.now(UTC)
        return cls(
            id=details_id or uuid4(),
            organization_id=organization_id,
            transaction_id=transaction_id,
            subtotal=subtotal,
            vat_amount=vat_amount,
            withheld_income_tax=wit,
            withheld_vat=wvat,
            other_taxes=other,
            total=total,
            calculation_source=TaxDetailCalculationSource(calculation_source),
            created_at=now,
            updated_at=now,
        )
