"""Map the projection outcome to a status label (SPEC-004 §21–22)."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.planning.domain.enums.projection import ProjectionStatus
from wealthos.modules.planning.domain.policies.safe_to_spend import SafeToSpendOutcome
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO

#: Spendable at or below this share of eligible cash is a thin margin.
LIMITED_MARGIN_RATIO = Decimal("0.05")


class ProjectionStatusPolicy:
    """``zero`` means "computed, no room"; ``insufficient_data`` means "unknown"."""

    def resolve(
        self,
        *,
        outcome: SafeToSpendOutcome,
        eligible_cash: Decimal,
        has_eligible_accounts: bool,
        critical_source_unavailable: bool = False,
    ) -> ProjectionStatus:
        if critical_source_unavailable:
            return ProjectionStatus.UNAVAILABLE
        if not has_eligible_accounts:
            return ProjectionStatus.INSUFFICIENT_DATA
        if outcome.breaches_reserve:
            return ProjectionStatus.DEFICIT
        if outcome.safe_to_spend <= ZERO:
            return ProjectionStatus.ZERO
        if eligible_cash > ZERO and outcome.safe_to_spend / eligible_cash <= LIMITED_MARGIN_RATIO:
            return ProjectionStatus.LIMITED
        return ProjectionStatus.HEALTHY
