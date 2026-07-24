"""SQLAlchemy implementation of AccountRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.accounts.domain.entities.account import Account
from wealthos.modules.accounts.infrastructure.mappers.account_mapper import AccountMapper
from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyAccountRepository(BaseRepository[AccountModel]):
    def __init__(self, session: Session, mapper: AccountMapper | None = None) -> None:
        super().__init__(session, AccountModel)
        self._mapper = mapper or AccountMapper()

    def add(self, account: Account) -> Account:
        model = self._mapper.to_model(account)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, account_id: UUID) -> Account | None:
        stmt = select(AccountModel).where(
            AccountModel.organization_id == organization_id,
            AccountModel.id == account_id,
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def get_many_for_update(
        self,
        organization_id: UUID,
        account_ids: list[UUID],
    ) -> list[Account]:
        if not account_ids:
            return []
        ordered_ids = sorted(set(account_ids))
        stmt = (
            select(AccountModel)
            .where(
                AccountModel.organization_id == organization_id,
                AccountModel.id.in_(ordered_ids),
            )
            .order_by(AccountModel.id.asc())
            .with_for_update()
        )
        models = list(self.session.scalars(stmt).all())
        return [self._mapper.to_entity(model) for model in models]

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[Account]:
        stmt = select(AccountModel).where(AccountModel.organization_id == organization_id)
        if not include_archived:
            stmt = stmt.where(AccountModel.is_active.is_(True))
        stmt = stmt.order_by(AccountModel.is_active.desc(), AccountModel.name.asc())
        models = self.session.scalars(stmt).all()
        return [self._mapper.to_entity(model) for model in models]

    def save(self, account: Account) -> Account:
        model = self.session.get(AccountModel, account.id)
        if model is None or model.organization_id != account.organization_id:
            raise LookupError("Account not found for save.")
        self._mapper.apply_to_model(account, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
