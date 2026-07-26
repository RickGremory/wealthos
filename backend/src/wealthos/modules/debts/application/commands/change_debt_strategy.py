"""ChangeDebtStrategyCommand — update organization payment strategy preference."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.debts.domain.exceptions import InvalidPayoffStrategy
from wealthos.modules.debts.domain.services.debt_strategy_service import ALLOWED_STRATEGIES
from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.exceptions import OrganizationNotFoundError
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)


@dataclass(frozen=True, slots=True)
class ChangeDebtStrategyInput:
    organization_id: UUID
    strategy: str


class ChangeDebtStrategyCommand:
    def __init__(self, organizations: OrganizationRepository) -> None:
        self._organizations = organizations

    def execute(self, data: ChangeDebtStrategyInput) -> Organization:
        cleaned = data.strategy.strip().lower()
        if cleaned not in ALLOWED_STRATEGIES:
            allowed = ", ".join(sorted(ALLOWED_STRATEGIES))
            raise InvalidPayoffStrategy(f"Strategy must be one of: {allowed}.")

        org = self._organizations.get_by_id(data.organization_id)
        if org is None:
            raise OrganizationNotFoundError("Organization not found.")

        org.change_debt_strategy(cleaned)
        return self._organizations.save(org)
