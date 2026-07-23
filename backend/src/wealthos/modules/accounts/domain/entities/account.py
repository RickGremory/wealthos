"""Account aggregate — financial container within an organization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from wealthos.modules.accounts.domain.exceptions import (
    AccountAlreadyArchived,
    InvalidLastFour,
)
from wealthos.modules.accounts.domain.value_objects.account_name import AccountName
from wealthos.modules.accounts.domain.value_objects.account_type import AccountType
from wealthos.shared.domain.value_objects.currency import Currency
from wealthos.shared.domain.value_objects.money import Money


def _normalize_last_four(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == "":
        return None
    if not cleaned.isdigit() or len(cleaned) != 4:
        raise InvalidLastFour("last_four must be exactly 4 digits.")
    return cleaned


def _normalize_institution(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@dataclass(slots=True)
class Account:
    """Financial account belonging to exactly one organization."""

    id: UUID
    organization_id: UUID
    name: AccountName
    account_type: AccountType
    currency: Currency
    opening_balance: Money
    current_balance: Money
    institution_name: str | None
    last_four: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    @classmethod
    def create(
        cls,
        *,
        organization_id: UUID,
        name: str,
        account_type: str,
        currency: str,
        opening_balance: Decimal | str | int = "0.00",
        institution_name: str | None = None,
        last_four: str | None = None,
        account_id: UUID | None = None,
    ) -> Account:
        now = datetime.now(UTC)
        money_currency = Currency(currency)
        opening = Money(opening_balance, money_currency)
        return cls(
            id=account_id or uuid4(),
            organization_id=organization_id,
            name=AccountName(name),
            account_type=AccountType(account_type),
            currency=money_currency,
            opening_balance=opening,
            current_balance=Money(opening.amount, money_currency),
            institution_name=_normalize_institution(institution_name),
            last_four=_normalize_last_four(last_four),
            is_active=True,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def rename(self, name: AccountName | str) -> None:
        self.name = name if isinstance(name, AccountName) else AccountName(name)
        self.updated_at = datetime.now(UTC)

    def change_institution(self, institution_name: str | None) -> None:
        self.institution_name = _normalize_institution(institution_name)
        self.updated_at = datetime.now(UTC)

    def change_last_four(self, last_four: str | None) -> None:
        self.last_four = _normalize_last_four(last_four)
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        if not self.is_active or self.archived_at is not None:
            raise AccountAlreadyArchived("Account is already archived.")
        now = datetime.now(UTC)
        self.is_active = False
        self.archived_at = now
        self.updated_at = now
