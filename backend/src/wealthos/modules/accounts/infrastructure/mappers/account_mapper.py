"""Map Account ↔ AccountModel."""

from __future__ import annotations

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.domain.value_objects.account_name import AccountName
from wealthos.modules.accounts.domain.value_objects.account_type import AccountType
from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.shared.base import BaseMapper
from wealthos.shared.domain.value_objects.currency import Currency
from wealthos.shared.domain.value_objects.money import Money


class AccountMapper(BaseMapper[AccountModel, Account]):
    def to_entity(self, model: AccountModel) -> Account:
        currency = Currency(model.currency)
        return Account(
            id=model.id,
            organization_id=model.organization_id,
            name=AccountName(model.name),
            account_type=AccountType(model.account_type),
            currency=currency,
            opening_balance=Money(model.opening_balance, currency),
            current_balance=Money(model.current_balance, currency),
            institution_name=model.institution_name,
            last_four=model.last_four,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )

    def to_model(self, entity: Account) -> AccountModel:
        return AccountModel(
            id=entity.id,
            organization_id=entity.organization_id,
            name=entity.name.value,
            account_type=entity.account_type.value,
            currency=entity.currency.value,
            opening_balance=entity.opening_balance.amount,
            current_balance=entity.current_balance.amount,
            institution_name=entity.institution_name,
            last_four=entity.last_four,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )

    def apply_to_model(self, entity: Account, model: AccountModel) -> AccountModel:
        model.name = entity.name.value
        model.account_type = entity.account_type.value
        model.currency = entity.currency.value
        model.opening_balance = entity.opening_balance.amount
        model.current_balance = entity.current_balance.amount
        model.institution_name = entity.institution_name
        model.last_four = entity.last_four
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at
        model.archived_at = entity.archived_at
        return model
