"""Account summary response schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from wealthos.modules.dashboard.application.views.account_balance import (
    AccountBalanceGroupView,
)


class DashboardAccountResponse(BaseModel):
    account_id: UUID
    name: str
    account_type: str
    classification: str
    institution_name: str | None
    current_balance: Decimal
    display_balance: Decimal
    is_active: bool


class AccountGroupResponse(BaseModel):
    currency: str
    accounts: list[DashboardAccountResponse]


class AccountSummaryResponse(BaseModel):
    """Current account balances grouped by currency.

    Liability display_balance is absolute; current_balance keeps the signed ledger value.
    """

    groups: list[AccountGroupResponse]

    @classmethod
    def from_views(
        cls,
        groups: list[AccountBalanceGroupView],
    ) -> AccountSummaryResponse:
        return cls(
            groups=[
                AccountGroupResponse(
                    currency=group.currency,
                    accounts=[
                        DashboardAccountResponse(
                            account_id=account.account_id,
                            name=account.name,
                            account_type=account.account_type,
                            classification=account.classification,
                            institution_name=account.institution_name,
                            current_balance=account.current_balance,
                            display_balance=account.display_balance,
                            is_active=account.is_active,
                        )
                        for account in group.accounts
                    ],
                )
                for group in groups
            ]
        )
