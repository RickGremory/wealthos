"""ArchiveTaxRule command."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.exceptions import TaxRuleNotFound
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository


@dataclass(frozen=True, slots=True)
class ArchiveTaxRuleInput:
    organization_id: UUID
    rule_id: UUID


class ArchiveTaxRuleCommand:
    def __init__(self, rules: TaxRuleRepository) -> None:
        self._rules = rules

    def execute(self, data: ArchiveTaxRuleInput) -> TaxRule:
        rule = self._rules.get_by_id(data.organization_id, data.rule_id)
        if rule is None:
            raise TaxRuleNotFound("Tax rule not found.")
        rule.archive()
        return self._rules.save(rule)
