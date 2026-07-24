"""Persistence port for TaxRule aggregates."""

from __future__ import annotations

from datetime import date
from typing import Protocol
from uuid import UUID

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule


class TaxRuleRepository(Protocol):
    def add(self, rule: TaxRule) -> TaxRule: ...

    def get_by_id(
        self,
        organization_id: UUID,
        rule_id: UUID,
    ) -> TaxRule | None: ...

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[TaxRule]: ...

    def list_active_for_period(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        period_from: date,
        period_to: date,
    ) -> list[TaxRule]: ...

    def save(self, rule: TaxRule) -> TaxRule: ...
