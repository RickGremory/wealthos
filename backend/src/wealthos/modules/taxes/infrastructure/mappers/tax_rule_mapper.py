"""Map TaxRule ↔ TaxRuleModel (+ category_ids)."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.value_objects.calculation_method import (
    TaxCalculationMethod,
)
from wealthos.modules.taxes.domain.value_objects.percentage import Percentage
from wealthos.modules.taxes.domain.value_objects.tax_base_type import TaxBaseType
from wealthos.modules.taxes.domain.value_objects.tax_inclusion_mode import (
    TaxInclusionMode,
)
from wealthos.modules.taxes.domain.value_objects.tax_rule_name import TaxRuleName
from wealthos.modules.taxes.domain.value_objects.tax_type import TaxType
from wealthos.modules.taxes.infrastructure.models.tax_models import TaxRuleModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.money import Money


class TaxRuleMapper(BaseMapper[TaxRuleModel, TaxRule]):
    def to_entity(
        self,
        model: TaxRuleModel,
        *,
        category_ids: tuple[UUID, ...] = (),
    ) -> TaxRule:
        currency = model.currency
        fixed = None
        if model.fixed_amount is not None and currency is not None:
            fixed = Money(model.fixed_amount, currency)
        return TaxRule(
            id=model.id,
            organization_id=model.organization_id,
            tax_profile_id=model.tax_profile_id,
            name=TaxRuleName(model.name),
            tax_type=TaxType(model.tax_type),
            calculation_method=TaxCalculationMethod(model.calculation_method),
            rate=Percentage(model.rate) if model.rate is not None else None,
            fixed_amount=fixed,
            applies_to=TaxBaseType(model.applies_to),
            tax_inclusion_mode=TaxInclusionMode(model.tax_inclusion_mode),
            category_ids=category_ids,
            priority=model.priority,
            is_active=model.is_active,
            effective_from=model.effective_from,
            effective_to=model.effective_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: TaxRule) -> TaxRuleModel:
        currency = None
        fixed_amount = None
        if entity.fixed_amount is not None:
            currency = entity.fixed_amount.currency.value
            fixed_amount = entity.fixed_amount.amount
        return TaxRuleModel(
            id=entity.id,
            organization_id=entity.organization_id,
            tax_profile_id=entity.tax_profile_id,
            name=entity.name.value,
            tax_type=entity.tax_type.value,
            calculation_method=entity.calculation_method.value,
            rate=entity.rate.value if entity.rate else None,
            fixed_amount=fixed_amount,
            currency=currency,
            applies_to=entity.applies_to.value,
            tax_inclusion_mode=entity.tax_inclusion_mode.value,
            priority=entity.priority,
            is_active=entity.is_active,
            effective_from=entity.effective_from,
            effective_to=entity.effective_to,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: TaxRule, model: TaxRuleModel) -> TaxRuleModel:
        model.name = entity.name.value
        model.rate = entity.rate.value if entity.rate else None
        if entity.fixed_amount is not None:
            model.fixed_amount = entity.fixed_amount.amount
            model.currency = entity.fixed_amount.currency.value
        model.applies_to = entity.applies_to.value
        model.tax_inclusion_mode = entity.tax_inclusion_mode.value
        model.priority = entity.priority
        model.is_active = entity.is_active
        model.effective_from = entity.effective_from
        model.effective_to = entity.effective_to
        model.updated_at = entity.updated_at
        model.archived_at = entity.archived_at
        return model
