"""SQLAlchemy CashPlanRepository (account_ids via cash_plan_accounts)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from wealthos.modules.planning.domain.entities.cash_plan import CashPlan
from wealthos.modules.planning.infrastructure.mappers.cash_plan_mapper import CashPlanMapper
from wealthos.modules.planning.infrastructure.models.planning_models import (
    CashPlanAccountModel,
    CashPlanModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyCashPlanRepository(BaseRepository[CashPlanModel]):
    def __init__(self, session: Session, mapper: CashPlanMapper | None = None) -> None:
        super().__init__(session, CashPlanModel)
        self._mapper = mapper or CashPlanMapper()

    def add(self, cash_plan: CashPlan) -> CashPlan:
        model = self._mapper.to_model(cash_plan)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, cash_plan_id: UUID) -> CashPlan | None:
        stmt = select(CashPlanModel).where(
            CashPlanModel.organization_id == organization_id,
            CashPlanModel.id == cash_plan_id,
        )
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        status: str | None = None,
        currency: str | None = None,
        include_archived: bool = False,
    ) -> list[CashPlan]:
        stmt = select(CashPlanModel).where(CashPlanModel.organization_id == organization_id)
        if status is not None:
            stmt = stmt.where(CashPlanModel.status == status)
        elif not include_archived:
            stmt = stmt.where(CashPlanModel.status != "archived")
        if currency is not None:
            stmt = stmt.where(CashPlanModel.currency == currency)
        stmt = stmt.order_by(CashPlanModel.created_at.desc())
        return [self._mapper.to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, cash_plan: CashPlan) -> CashPlan:
        model = self.session.get(CashPlanModel, cash_plan.id)
        if model is None or model.organization_id != cash_plan.organization_id:
            raise LookupError("Cash plan not found for save.")
        self._mapper.apply_to_model(cash_plan, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list_account_ids(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
    ) -> list[UUID]:
        plan = self.session.get(CashPlanModel, cash_plan_id)
        if plan is None or plan.organization_id != organization_id:
            return []
        stmt = (
            select(CashPlanAccountModel.account_id)
            .where(CashPlanAccountModel.cash_plan_id == cash_plan_id)
            .order_by(CashPlanAccountModel.account_id.asc())
        )
        return list(self.session.scalars(stmt).all())

    def replace_account_ids(
        self,
        organization_id: UUID,
        cash_plan_id: UUID,
        account_ids: list[UUID],
    ) -> None:
        plan = self.session.get(CashPlanModel, cash_plan_id)
        if plan is None or plan.organization_id != organization_id:
            raise LookupError("Cash plan not found for replace_account_ids.")
        self.session.execute(
            delete(CashPlanAccountModel).where(CashPlanAccountModel.cash_plan_id == cash_plan_id)
        )
        seen: set[UUID] = set()
        for account_id in account_ids:
            if account_id in seen:
                continue
            seen.add(account_id)
            self.session.add(CashPlanAccountModel(cash_plan_id=cash_plan_id, account_id=account_id))
        self.flush()
