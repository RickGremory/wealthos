"""UpdateTaxRule command."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.exceptions import TaxRuleNotFound
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository
from wealthos.shared.domain.value_objects.money import Money


@dataclass(frozen=True, slots=True)
class UpdateTaxRuleInput:
    organization_id: UUID
    rule_id: UUID
    name: str | None = None
    rate: Decimal | None = None
    fixed_amount: Decimal | None = None
    priority: int | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    clear_effective_to: bool = False
    category_ids: tuple[UUID, ...] | list[UUID] | None = None
    fields_set: frozenset[str] | None = None


class UpdateTaxRuleCommand:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        rules: TaxRuleRepository,
    ) -> None:
        self._profiles = profiles
        self._rules = rules

    def execute(self, data: UpdateTaxRuleInput) -> TaxRule:
        rule = self._rules.get_by_id(data.organization_id, data.rule_id)
        if rule is None:
            raise TaxRuleNotFound("Tax rule not found.")

        profile = self._profiles.get_by_id(data.organization_id, rule.tax_profile_id)
        currency = profile.currency.value if profile else "MXN"

        fields = data.fields_set or frozenset()
        if "name" in fields and data.name is not None:
            rule.rename(data.name)
        if "rate" in fields and data.rate is not None:
            rule.change_rate(data.rate)
        if "fixed_amount" in fields and data.fixed_amount is not None:
            rule.change_fixed_amount(Money(data.fixed_amount, currency))
        if "priority" in fields and data.priority is not None:
            rule.change_priority(data.priority)
        if "effective_from" in fields or "effective_to" in fields or data.clear_effective_to:
            rule.change_effective_window(
                effective_from=data.effective_from,
                effective_to=data.effective_to,
                clear_effective_to=data.clear_effective_to,
            )
        if "category_ids" in fields and data.category_ids is not None:
            rule.replace_categories(data.category_ids)

        return self._rules.save(rule)
