"""Cash plan alert schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, field_serializer

from wealthos.modules.planning.application.services.cash_alert_service import CashAlert


class CashAlertResponse(BaseModel):
    type: str
    severity: str
    date: date | None
    amount: Decimal | None
    message: str

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return format(value, "f")

    @classmethod
    def from_alert(cls, alert: CashAlert) -> CashAlertResponse:
        return cls(
            type=alert.type,
            severity=alert.severity,
            date=alert.date,
            amount=alert.amount,
            message=alert.message,
        )


class CashAlertListResponse(BaseModel):
    items: list[CashAlertResponse]
    total: int
