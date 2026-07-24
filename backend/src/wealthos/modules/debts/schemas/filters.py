"""Debt list filter query params."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from wealthos.modules.debts.schemas.create import DebtTypeLiteral


class DebtListFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["active", "paid_off", "archived"] | None = None
    debt_type: DebtTypeLiteral | None = None
    currency: str | None = None
    include_archived: bool = False
