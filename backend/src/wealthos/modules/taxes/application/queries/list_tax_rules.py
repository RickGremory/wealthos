"""ListTaxRules query."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.exceptions import TaxProfileNotFound
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository


class ListTaxRulesQuery:
    def __init__(
        self,
        profiles: TaxProfileRepository,
        rules: TaxRuleRepository,
    ) -> None:
        self._profiles = profiles
        self._rules = rules

    def execute(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[TaxRule]:
        profile = self._profiles.get_by_id(organization_id, tax_profile_id)
        if profile is None:
            raise TaxProfileNotFound("Tax profile not found.")
        return self._rules.list_by_profile(
            organization_id,
            tax_profile_id,
            include_archived=include_archived,
        )
