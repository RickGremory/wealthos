"""Derive cash-plan alerts from a projection and context inputs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from wealthos.modules.planning.application.services.cash_projection_service import (
    CashProjection,
)

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class OverdueInflow:
    expected_date: date
    amount: Decimal
    description: str | None = None


@dataclass(frozen=True, slots=True)
class CashAlert:
    type: str
    severity: str  # info, warning, critical
    date: date | None
    amount: Decimal | None
    message: str


class CashAlertService:
    """Build alerts from CashProjection + buffer + overdue inflows."""

    def generate(
        self,
        *,
        projection: CashProjection,
        minimum_cash_buffer: Decimal,
        overdue_inflows: tuple[OverdueInflow, ...] | list[OverdueInflow] = (),
        as_of: date | None = None,
        large_outflow_threshold: Decimal | None = None,
    ) -> tuple[CashAlert, ...]:
        alerts: list[CashAlert] = []
        buffer = _money(minimum_cash_buffer)

        if projection.first_shortfall_date is not None:
            shortfall_amount = _ZERO
            for point in projection.points:
                if point.date == projection.first_shortfall_date:
                    shortfall_amount = abs(min(point.lowest_intraday_balance, point.ending_balance))
                    break
            alerts.append(
                CashAlert(
                    type="cash_shortfall",
                    severity="critical",
                    date=projection.first_shortfall_date,
                    amount=_money(shortfall_amount),
                    message="El saldo proyectado será negativo.",
                )
            )

        for point in projection.points:
            if point.ending_balance < _ZERO:
                continue
            if buffer > _ZERO and point.ending_balance < buffer:
                alerts.append(
                    CashAlert(
                        type="low_cash_buffer",
                        severity="warning",
                        date=point.date,
                        amount=_money(point.ending_balance),
                        message="El saldo proyectado cae por debajo del buffer mínimo.",
                    )
                )
                break

        if large_outflow_threshold is not None:
            threshold = _money(large_outflow_threshold)
            for point in projection.points:
                if point.outflows >= threshold > _ZERO:
                    alerts.append(
                        CashAlert(
                            type="large_outflow",
                            severity="warning",
                            date=point.date,
                            amount=point.outflows,
                            message="Se proyecta una salida de efectivo grande.",
                        )
                    )

        today = as_of
        for overdue in overdue_inflows:
            if today is not None and overdue.expected_date >= today:
                continue
            desc = overdue.description or "ingreso esperado"
            alerts.append(
                CashAlert(
                    type="overdue_inflow",
                    severity="warning",
                    date=overdue.expected_date,
                    amount=_money(overdue.amount),
                    message=f"Ingreso vencido sin match: {desc}.",
                )
            )

        return tuple(alerts)


def _money(value: Decimal | int | str) -> Decimal:
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)
