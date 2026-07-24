"""SQLAlchemy implementation of GoalRepository."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, selectinload

from wealthos.modules.accounts.infrastructure.models.account_model import AccountModel
from wealthos.modules.goals.domain.entities.goal import Goal
from wealthos.modules.goals.infrastructure.mappers.goal_mapper import GoalMapper
from wealthos.modules.goals.infrastructure.models.goal_model import (
    GoalManualProgressModel,
    GoalModel,
)
from wealthos.modules.transactions.infrastructure.models.transaction_model import (
    TransactionEntryModel,
    TransactionModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyGoalRepository(BaseRepository[GoalModel]):
    def __init__(self, session: Session, mapper: GoalMapper | None = None) -> None:
        super().__init__(session, GoalModel)
        self._mapper = mapper or GoalMapper()

    def add(self, goal: Goal) -> Goal:
        model = self._mapper.to_model(goal)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_by_id(self, organization_id: UUID, goal_id: UUID) -> Goal | None:
        stmt = (
            select(GoalModel)
            .options(
                selectinload(GoalModel.account_links),
                selectinload(GoalModel.manual_progress),
            )
            .where(
                GoalModel.organization_id == organization_id,
                GoalModel.id == goal_id,
            )
        )
        model = self.session.scalars(stmt).first()
        if model is None:
            return None
        return self._mapper.to_entity(model)

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[Goal]:
        stmt = (
            select(GoalModel)
            .options(
                selectinload(GoalModel.account_links),
                selectinload(GoalModel.manual_progress),
            )
            .where(GoalModel.organization_id == organization_id)
        )
        if not include_archived:
            stmt = stmt.where(GoalModel.status != "archived")
        stmt = stmt.order_by(GoalModel.created_at.desc())
        models = self.session.scalars(stmt).all()
        return [self._mapper.to_entity(model) for model in models]

    def save(self, goal: Goal) -> Goal:
        model = self.session.get(
            GoalModel,
            goal.id,
            options=(
                selectinload(GoalModel.account_links),
                selectinload(GoalModel.manual_progress),
            ),
        )
        if model is None or model.organization_id != goal.organization_id:
            raise LookupError("Goal not found for save.")
        self._mapper.apply_to_model(goal, model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get_manual_progress(self, goal_id: UUID) -> Decimal | None:
        model = self.session.get(GoalManualProgressModel, goal_id)
        if model is None:
            return None
        return Decimal(str(model.current_amount))

    def set_manual_progress(self, goal_id: UUID, amount: Decimal) -> None:
        model = self.session.get(GoalManualProgressModel, goal_id)
        now = datetime.now(UTC)
        if model is None:
            self.session.add(
                GoalManualProgressModel(
                    goal_id=goal_id,
                    current_amount=amount,
                    updated_at=now,
                )
            )
        else:
            model.current_amount = amount
            model.updated_at = now
        self.flush()

    def sum_account_balances(
        self,
        organization_id: UUID,
        account_ids: tuple[UUID, ...],
        currency: str,
    ) -> Decimal:
        if not account_ids:
            return Decimal("0.00")
        stmt = select(func.coalesce(func.sum(AccountModel.current_balance), 0)).where(
            AccountModel.organization_id == organization_id,
            AccountModel.id.in_(account_ids),
            AccountModel.currency == currency,
            AccountModel.is_active.is_(True),
        )
        return Decimal(str(self.session.scalar(stmt) or 0))

    def average_daily_savings(
        self,
        organization_id: UUID,
        *,
        currency: str,
        account_ids: tuple[UUID, ...] | None,
        days: int = 90,
    ) -> Decimal:
        """Average net entry flow per day over the lookback window.

        Starts from ``transactions`` so Postgres can use
        ``(organization_id, status, occurred_at)`` instead of scanning all entries.
        """
        if account_ids is not None and not account_ids:
            return Decimal("0.00")

        since = datetime.now(UTC) - timedelta(days=days)
        stmt = (
            select(func.coalesce(func.sum(TransactionEntryModel.amount), 0))
            .select_from(TransactionModel)
            .join(
                TransactionEntryModel,
                TransactionEntryModel.transaction_id == TransactionModel.id,
            )
            .join(AccountModel, AccountModel.id == TransactionEntryModel.account_id)
            .where(
                TransactionModel.organization_id == organization_id,
                TransactionModel.status == "posted",
                TransactionModel.occurred_at >= since,
                TransactionEntryModel.currency == currency,
                AccountModel.currency == currency,
            )
        )
        if account_ids is not None:
            stmt = stmt.where(TransactionEntryModel.account_id.in_(account_ids))
        total = Decimal(str(self.session.scalar(stmt) or 0))
        return (total / Decimal(days)).quantize(Decimal("0.01"))

    def net_worth_for_currency(
        self,
        organization_id: UUID,
        currency: str,
    ) -> Decimal:
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        (
                            AccountModel.classification == "asset",
                            AccountModel.current_balance,
                        ),
                        else_=0,
                    )
                ),
                0,
            )
            - func.coalesce(
                func.sum(
                    case(
                        (
                            AccountModel.classification == "liability",
                            func.abs(AccountModel.current_balance),
                        ),
                        else_=0,
                    )
                ),
                0,
            )
        ).where(
            AccountModel.organization_id == organization_id,
            AccountModel.currency == currency,
            AccountModel.is_active.is_(True),
        )
        return Decimal(str(self.session.scalar(stmt) or 0))
