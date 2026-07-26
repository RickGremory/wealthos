"""ChangeDebtStrategyCommand — update organization payment strategy preference."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from uuid import UUID

from wealthos.modules.debts.domain.exceptions import InvalidPayoffStrategy
from wealthos.modules.debts.domain.services.debt_strategy_service import ALLOWED_STRATEGIES
from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.exceptions import OrganizationNotFoundError
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)

logger = logging.getLogger(__name__)


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

        previous = org.debt_strategy
        org.change_debt_strategy(cleaned)
        saved = self._organizations.save(org)
        logger.info(
            "audit.payment_strategy_changed",
            extra={
                "organization_id": str(data.organization_id),
                "resource_type": "organization",
                "resource_id": str(data.organization_id),
                "action": "strategy_changed",
                "from_strategy": previous,
                "to_strategy": cleaned,
            },
        )
        return saved
