"""Map TaxCalculation ↔ TaxCalculationModel (+ lines)."""

from __future__ import annotations

from wealthos.modules.taxes.domain.entities.tax_calculation import (
    TaxCalculation,
    TaxCalculationLine,
)
from wealthos.modules.taxes.domain.value_objects.tax_calculation_status import (
    TaxCalculationStatus,
)
from wealthos.modules.taxes.infrastructure.models.tax_models import (
    TaxCalculationLineModel,
    TaxCalculationModel,
)
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class TaxCalculationMapper(BaseMapper[TaxCalculationModel, TaxCalculation]):
    def to_entity(
        self,
        model: TaxCalculationModel,
        *,
        lines: list[TaxCalculationLine] | None = None,
    ) -> TaxCalculation:
        currency = model.currency
        return TaxCalculation(
            id=model.id,
            organization_id=model.organization_id,
            tax_period_id=model.tax_period_id,
            version=model.version,
            status=TaxCalculationStatus(model.status),
            gross_income=Money(model.gross_income, currency),
            taxable_income=Money(model.taxable_income, currency),
            deductible_expenses=Money(model.deductible_expenses, currency),
            taxable_base=Money(model.taxable_base, currency),
            estimated_tax=Money(model.estimated_tax, currency),
            calculated_at=model.calculated_at,
            calculated_by_user_id=model.calculated_by_user_id,
            lines=list(lines or ()),
        )

    def line_to_entity(self, model: TaxCalculationLineModel) -> TaxCalculationLine:
        return TaxCalculationLine(
            id=model.id,
            tax_calculation_id=model.tax_calculation_id,
            tax_rule_id=model.tax_rule_id,
            description=model.description,
            taxable_base=Money(model.taxable_base, model.currency),
            rate=model.rate,
            calculated_amount=Money(model.calculated_amount, model.currency),
        )

    def to_model(self, entity: TaxCalculation) -> TaxCalculationModel:
        currency = entity.estimated_tax.currency.value
        return TaxCalculationModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_period_id=entity.tax_period_id,
            version=entity.version,
            status=entity.status.value,
            gross_income=entity.gross_income.amount,
            taxable_income=entity.taxable_income.amount,
            deductible_expenses=entity.deductible_expenses.amount,
            taxable_base=entity.taxable_base.amount,
            estimated_tax=entity.estimated_tax.amount,
            currency=currency,
            calculated_at=entity.calculated_at,
            calculated_by_user_id=entity.calculated_by_user_id,
        )

    def line_to_model(self, line: TaxCalculationLine) -> TaxCalculationLineModel:
        currency = line.calculated_amount.currency.value
        return TaxCalculationLineModel(
            id=line.id,
            tax_calculation_id=line.tax_calculation_id,
            tax_rule_id=line.tax_rule_id,
            description=line.description,
            taxable_base=line.taxable_base.amount,
            rate=line.rate,
            calculated_amount=line.calculated_amount.amount,
            currency=currency,
        )
