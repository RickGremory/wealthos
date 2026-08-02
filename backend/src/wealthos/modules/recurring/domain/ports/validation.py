"""Validation ports used by Recurring application commands."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from wealthos.modules.recurring.domain.enums.rule import RecurringDirection


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    id: UUID
    organization_id: UUID
    currency: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class CategorySnapshot:
    id: UUID
    organization_id: UUID
    is_active: bool


@dataclass(frozen=True, slots=True)
class TransactionSnapshot:
    id: UUID
    organization_id: UUID
    amount: Decimal
    currency: str
    is_voided: bool


class RecurringAccountValidationPort(Protocol):
    def get_account(
        self,
        organization_id: UUID,
        account_id: UUID,
    ) -> AccountSnapshot | None: ...

    def validate_for_rule(
        self,
        organization_id: UUID,
        direction: RecurringDirection,
        account_id: UUID | None,
        destination_account_id: UUID | None,
        currency: str,
    ) -> None: ...


class RecurringCategoryValidationPort(Protocol):
    def get_category(
        self,
        organization_id: UUID,
        category_id: UUID,
    ) -> CategorySnapshot | None: ...


class RecurringTransactionValidationPort(Protocol):
    def get_transaction(
        self,
        organization_id: UUID,
        transaction_id: UUID,
    ) -> TransactionSnapshot | None: ...
