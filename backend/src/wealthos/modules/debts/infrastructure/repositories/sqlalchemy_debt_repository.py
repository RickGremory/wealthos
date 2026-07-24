"""SQLAlchemy DebtRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from wealthos.modules.debts.domain.entities.debt import Debt
from wealthos.modules.debts.infrastructure.mappers.debt_mapper import DebtMapper
from wealthos.modules.debts.infrastructure.models.debt_model import DebtModel
from wealthos.shared.base import BaseRepository


class SqlAlchemyDebtRepository(BaseRepository[DebtModel]):
    def __init__(self, session: Session, mapper: DebtMapper | None = None) -> None:
        super().__init__(session, DebtModel)
        self._mapper = mapper or DebtMapper()

    def add(self, debt: Debt) -> Debt:
        model = self._mapper.to_model(debt)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, debt_id: UUID) -> Debt | None:
        stmt = select(DebtModel).where(
            DebtModel.organization_id == organization_id,
            DebtModel.id == debt_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def get_active_by_account(
        self,
        organization_id: UUID,
        account_id: UUID,
    ) -> Debt | None:
        stmt = select(DebtModel).where(
            DebtModel.organization_id == organization_id,
            DebtModel.account_id == account_id,
            DebtModel.status.in_(("active", "paid_off")),
            DebtModel.archived_at.is_(None),
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        debt_type: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[Debt]:
        stmt = select(DebtModel).where(DebtModel.organization_id == organization_id)
        if status is not None:
            stmt = stmt.where(DebtModel.status == status)
        elif not include_archived:
            stmt = stmt.where(DebtModel.status != "archived")
        if debt_type is not None:
            stmt = stmt.where(DebtModel.debt_type == debt_type)
        if currency is not None:
            stmt = stmt.where(DebtModel.currency == currency)
        stmt = stmt.order_by(DebtModel.created_at.desc())
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, debt: Debt) -> Debt:
        model = self.session.get(DebtModel, debt.id)
        if model is None or model.organization_id != debt.organization_id:
            raise LookupError("Debt not found for save.")
        self._mapper.apply_to_model(debt, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)
