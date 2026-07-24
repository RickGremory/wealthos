"""Mexico category mapping and transaction override entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.tax_mx.domain.value_objects.mexico_expense_treatment import (
    MexicoExpenseTreatment,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_income_treatment import (
    MexicoIncomeTreatment,
)
from wealthos.modules.tax_mx.domain.value_objects.mexico_vat_treatment import (
    MexicoVATTreatment,
)
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage


@dataclass(slots=True)
class MexicoTaxCategoryMapping:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    category_id: UUID
    income_treatment: MexicoIncomeTreatment | None
    expense_treatment: MexicoExpenseTreatment | None
    vat_treatment: MexicoVATTreatment
    deductibility_percentage: Percentage
    vat_creditable_percentage: Percentage
    requires_cfdi: bool
    requires_payment_evidence: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        category_id: UUID,
        vat_treatment: str,
        deductibility_percentage: Decimal = Decimal("100"),
        vat_creditable_percentage: Decimal = Decimal("100"),
        income_treatment: str | None = None,
        expense_treatment: str | None = None,
        requires_cfdi: bool = False,
        requires_payment_evidence: bool = False,
        mapping_id: UUID | None = None,
    ) -> MexicoTaxCategoryMapping:
        now = datetime.now(UTC)
        return cls(
            id=mapping_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            category_id=category_id,
            income_treatment=(
                MexicoIncomeTreatment(income_treatment) if income_treatment else None
            ),
            expense_treatment=(
                MexicoExpenseTreatment(expense_treatment) if expense_treatment else None
            ),
            vat_treatment=MexicoVATTreatment(vat_treatment),
            deductibility_percentage=Percentage(deductibility_percentage, max_value=Decimal("100")),
            vat_creditable_percentage=Percentage(
                vat_creditable_percentage, max_value=Decimal("100")
            ),
            requires_cfdi=requires_cfdi,
            requires_payment_evidence=requires_payment_evidence,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        vat_treatment: str | None = None,
        income_treatment: str | None = None,
        expense_treatment: str | None = None,
        deductibility_percentage: Decimal | None = None,
        vat_creditable_percentage: Decimal | None = None,
        requires_cfdi: bool | None = None,
        requires_payment_evidence: bool | None = None,
        clear_income_treatment: bool = False,
        clear_expense_treatment: bool = False,
        fields_set: frozenset[str] | None = None,
    ) -> None:
        fields = fields_set or frozenset()
        if "vat_treatment" in fields and vat_treatment is not None:
            self.vat_treatment = MexicoVATTreatment(vat_treatment)
        if clear_income_treatment:
            self.income_treatment = None
        elif "income_treatment" in fields and income_treatment is not None:
            self.income_treatment = MexicoIncomeTreatment(income_treatment)
        if clear_expense_treatment:
            self.expense_treatment = None
        elif "expense_treatment" in fields and expense_treatment is not None:
            self.expense_treatment = MexicoExpenseTreatment(expense_treatment)
        if "deductibility_percentage" in fields and deductibility_percentage is not None:
            self.deductibility_percentage = Percentage(
                deductibility_percentage, max_value=Decimal("100")
            )
        if "vat_creditable_percentage" in fields and vat_creditable_percentage is not None:
            self.vat_creditable_percentage = Percentage(
                vat_creditable_percentage, max_value=Decimal("100")
            )
        if "requires_cfdi" in fields and requires_cfdi is not None:
            self.requires_cfdi = requires_cfdi
        if "requires_payment_evidence" in fields and requires_payment_evidence is not None:
            self.requires_payment_evidence = requires_payment_evidence
        self.updated_at = datetime.now(UTC)


@dataclass(slots=True)
class MexicoTaxTransactionOverride:
    id: UUID
    organization_id: UUID
    tax_profile_id: UUID
    transaction_id: UUID
    income_treatment: MexicoIncomeTreatment | None
    expense_treatment: MexicoExpenseTreatment | None
    vat_treatment: MexicoVATTreatment
    deductibility_percentage: Percentage
    vat_creditable_percentage: Percentage
    requires_cfdi: bool
    reason: str | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_profile_id: UUID,
        transaction_id: UUID,
        vat_treatment: str,
        created_by_user_id: UUID,
        deductibility_percentage: Decimal = Decimal("100"),
        vat_creditable_percentage: Decimal = Decimal("100"),
        income_treatment: str | None = None,
        expense_treatment: str | None = None,
        requires_cfdi: bool = False,
        reason: str | None = None,
        override_id: UUID | None = None,
    ) -> MexicoTaxTransactionOverride:
        now = datetime.now(UTC)
        return cls(
            id=override_id or uuid4(),
            organization_id=organization_id,
            tax_profile_id=tax_profile_id,
            transaction_id=transaction_id,
            income_treatment=(
                MexicoIncomeTreatment(income_treatment) if income_treatment else None
            ),
            expense_treatment=(
                MexicoExpenseTreatment(expense_treatment) if expense_treatment else None
            ),
            vat_treatment=MexicoVATTreatment(vat_treatment),
            deductibility_percentage=Percentage(deductibility_percentage, max_value=Decimal("100")),
            vat_creditable_percentage=Percentage(
                vat_creditable_percentage, max_value=Decimal("100")
            ),
            requires_cfdi=requires_cfdi,
            reason=reason.strip() if reason else None,
            created_by_user_id=created_by_user_id,
            created_at=now,
            updated_at=now,
        )
