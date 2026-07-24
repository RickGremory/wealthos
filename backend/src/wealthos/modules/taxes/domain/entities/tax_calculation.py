"""TaxCalculation snapshot + explanatory lines."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.value_objects.tax_calculation_status import (
    TaxCalculationStatus,
)
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class TaxCalculationLine:
    id: UUID
    tax_calculation_id: UUID
    tax_rule_id: UUID
    description: str
    taxable_base: Money
    rate: Decimal | None
    calculated_amount: Money


@dataclass(slots=True)
class TaxCalculation:
    id: UUID
    organization_id: UUID
    tax_period_id: UUID
    version: int
    status: TaxCalculationStatus
    gross_income: Money
    taxable_income: Money
    deductible_expenses: Money
    taxable_base: Money
    estimated_tax: Money
    calculated_at: datetime
    calculated_by_user_id: UUID
    lines: list[TaxCalculationLine] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        tax_period_id: UUID,
        version: int,
        gross_income: Money,
        taxable_income: Money,
        deductible_expenses: Money,
        taxable_base: Money,
        estimated_tax: Money,
        calculated_by_user_id: UUID,
        lines: list[TaxCalculationLine] | None = None,
        calculation_id: UUID | None = None,
    ) -> TaxCalculation:
        calc_id = calculation_id or uuid4()
        return cls(
            id=calc_id,
            organization_id=organization_id,
            tax_period_id=tax_period_id,
            version=version,
            status=TaxCalculationStatus("completed"),
            gross_income=gross_income,
            taxable_income=taxable_income,
            deductible_expenses=deductible_expenses,
            taxable_base=taxable_base,
            estimated_tax=estimated_tax,
            calculated_at=datetime.now(UTC),
            calculated_by_user_id=calculated_by_user_id,
            lines=list(lines or ()),
        )

    def supersede(self) -> None:
        self.status = TaxCalculationStatus("superseded")
