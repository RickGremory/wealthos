"""CreateTaxRule command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.exceptions import TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class CreateTaxRuleInput:
    organization_id: UUID
    tax_profile_id: UUID
    name: str
    tax_type: str
    calculation_method: str
    applies_to: str
    effective_from: date
    rate: Decimal | None = None
    fixed_amount: Decimal | None = None
    tax_inclusion_mode: str = "exclusive"
    category_ids: tuple[UUID, ...] | list[UUID] = ()
    priority: int = 100
    effective_to: date | None = None


class CreateTaxRuleCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        rules: TaxRuleRepository,
    ) -> None:
        self._profiles = profiles
        self._rules = rules

    def execute(self, data: CreateTaxRuleInput) -> TaxRule:
        profile = self._profiles.get_by_id(data.organization_id, data.tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")

        fixed = None
        if data.fixed_amount is not None:
            fixed = Money(data.fixed_amount, profile.currency.value)

        rule = TaxRule.create(
            organization_id=data.organization_id,
            tax_profile_id=data.tax_profile_id,
            name=data.name,
            tax_type=data.tax_type,
            calculation_method=data.calculation_method,
            applies_to=data.applies_to,
            effective_from=data.effective_from,
            rate=data.rate,
            fixed_amount=fixed,
            tax_inclusion_mode=data.tax_inclusion_mode,
            category_ids=data.category_ids,
            priority=data.priority,
            effective_to=data.effective_to,
        )
        return self._rules.add(rule)
