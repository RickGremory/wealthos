"""Resolve the minimum balance the projection must never breach (§15)."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from wealthos.modules.planning.domain.entities.planning_settings import PlanningSettings
from wealthos.modules.planning.domain.enums.alert import PlanningAlertCode
from wealthos.modules.planning.domain.enums.reservation import (
    ReservationType,
    SafetyReserveStrategy,
)
from wealthos.modules.planning.domain.value_objects.money_utils import ZERO, quantize_money
from wealthos.modules.planning.domain.value_objects.reservation import (
    PlanningReservation,
    SafetyReserveResult,
)


class SafetyReservePolicy:
    """No reserve configured still calculates — it just lowers confidence."""

    def resolve(
        self,
        settings: PlanningSettings,
        reservations: Iterable[PlanningReservation],
    ) -> SafetyReserveResult:
        strategy = settings.safety_reserve_strategy

        if strategy is SafetyReserveStrategy.FIXED_AMOUNT:
            amount = quantize_money(settings.safety_reserve_amount or ZERO)
            return SafetyReserveResult(
                strategy=strategy,
                required_amount=amount,
                label="safety_reserve.fixed_amount",
            )

        if strategy is SafetyReserveStrategy.LINKED_GOAL:
            return self._from_linked_goal(settings, reservations)

        if not strategy.is_supported:
            return SafetyReserveResult(
                strategy=strategy,
                required_amount=ZERO,
                label="safety_reserve.unsupported",
                reason_codes=(PlanningAlertCode.SAFETY_RESERVE_STRATEGY_UNSUPPORTED.value,),
            )

        return SafetyReserveResult(
            strategy=SafetyReserveStrategy.NONE,
            required_amount=ZERO,
            label="safety_reserve.none",
            reason_codes=(PlanningAlertCode.SAFETY_RESERVE_NOT_CONFIGURED.value,),
        )

    def _from_linked_goal(
        self,
        settings: PlanningSettings,
        reservations: Iterable[PlanningReservation],
    ) -> SafetyReserveResult:
        goal_id = str(settings.linked_emergency_goal_id) if settings.linked_emergency_goal_id else None
        for reservation in reservations:
            if reservation.reservation_type is not ReservationType.GOAL:
                continue
            if goal_id is not None and reservation.source.resource_id != goal_id:
                continue
            return SafetyReserveResult(
                strategy=SafetyReserveStrategy.LINKED_GOAL,
                required_amount=quantize_money(reservation.outstanding_amount),
                label=reservation.label,
                source_reservation_key=reservation.occurrence_key,
            )

        return SafetyReserveResult(
            strategy=SafetyReserveStrategy.LINKED_GOAL,
            required_amount=ZERO,
            label="safety_reserve.linked_goal",
            reason_codes=(PlanningAlertCode.SAFETY_RESERVE_GOAL_UNAVAILABLE.value,),
        )

    def other_reserved_funds(
        self,
        reservations: Iterable[PlanningReservation],
        *,
        currency: str,
        exclude_key: str | None = None,
    ) -> Decimal:
        """Reserved money (tax pending, protected goals) also has to stay put."""
        code = currency.strip().upper()
        total = ZERO
        for reservation in reservations:
            if reservation.currency.strip().upper() != code:
                continue
            if exclude_key is not None and reservation.occurrence_key == exclude_key:
                continue
            total += max(reservation.outstanding_amount, ZERO)
        return quantize_money(total)
