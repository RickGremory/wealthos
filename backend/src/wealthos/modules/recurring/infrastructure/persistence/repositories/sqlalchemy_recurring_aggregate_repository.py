"""SQLAlchemy RecurringAggregateRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringDirection,
    RecurringRuleStatus,
    RecurringSourceType,
)
from wealthos.modules.recurring.domain.exceptions import RecurringConcurrentUpdate
from wealthos.modules.recurring.domain.ports.repositories import (
    RecurringRuleFilters,
    RecurringRuleListProjection,
)
from wealthos.modules.recurring.infrastructure.persistence.mappers.recurring_aggregate_mapper import (
    RecurringAggregateMapper,
)
from wealthos.modules.recurring.infrastructure.persistence.models.recurring_models import (
    RecurringRuleModel,
    RecurringRuleVersionModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyRecurringAggregateRepository(BaseRepository[RecurringRuleModel]):
    def __init__(
        self,
        session: Session,
        mapper: RecurringAggregateMapper | None = None,
    ) -> None:
        super().__init__(session, RecurringRuleModel)
        self._mapper = mapper or RecurringAggregateMapper()

    def add(self, aggregate: RecurringAggregate) -> RecurringAggregate:
        model = self._mapper.to_model(aggregate)
        super().add(model)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def get(
        self,
        organization_id: UUID,
        rule_id: UUID,
        *,
        for_update: bool = False,
    ) -> RecurringAggregate | None:
        stmt = (
            select(RecurringRuleModel)
            .where(
                RecurringRuleModel.organization_id == organization_id,
                RecurringRuleModel.id == rule_id,
            )
            .options(
                selectinload(RecurringRuleModel.versions),
                selectinload(RecurringRuleModel.pauses),
                selectinload(RecurringRuleModel.exceptions),
            )
        )
        if for_update:
            stmt = stmt.with_for_update()
        model = self.session.scalars(stmt).first()
        return self._mapper.to_entity(model) if model else None

    def save(
        self,
        aggregate: RecurringAggregate,
        expected_version: int,
    ) -> RecurringAggregate:
        model = self.session.get(RecurringRuleModel, aggregate.id)
        if model is None or model.organization_id != aggregate.organization_id:
            raise LookupError("Recurring rule not found for save.")
        if model.version != expected_version:
            raise RecurringConcurrentUpdate(
                "The recurring rule was modified by another request. Refresh and try again."
            )
        if aggregate.version != expected_version + 1:
            raise RecurringConcurrentUpdate(
                "The recurring rule was modified by another request. Refresh and try again."
            )
        self._mapper.apply_to_model(model, aggregate)
        self.flush()
        self.refresh(model)
        return self._mapper.to_entity(model)

    def list(
        self,
        organization_id: UUID,
        filters: RecurringRuleFilters,
    ) -> list[RecurringRuleListProjection]:
        stmt = (
            select(RecurringRuleModel, RecurringRuleVersionModel)
            .join(
                RecurringRuleVersionModel,
                RecurringRuleVersionModel.recurring_rule_id == RecurringRuleModel.id,
            )
            .where(RecurringRuleModel.organization_id == organization_id)
            .where(RecurringRuleVersionModel.effective_until.is_(None))
        )
        if filters.status is not None:
            stmt = stmt.where(RecurringRuleModel.status == filters.status.value)
        elif not filters.include_archived:
            stmt = stmt.where(RecurringRuleModel.status != RecurringRuleStatus.ARCHIVED.value)
        if filters.source_type is not None:
            stmt = stmt.where(RecurringRuleModel.source_type == filters.source_type.value)
        if filters.direction is not None:
            stmt = stmt.where(RecurringRuleVersionModel.direction == filters.direction.value)
        if filters.currency is not None:
            stmt = stmt.where(RecurringRuleVersionModel.currency == filters.currency)
        if filters.account_id is not None:
            stmt = stmt.where(RecurringRuleVersionModel.account_id == filters.account_id)

        stmt = stmt.order_by(RecurringRuleModel.updated_at.desc())
        rows = self.session.execute(stmt).all()
        results: list[RecurringRuleListProjection] = []
        seen: set[UUID] = set()
        for rule_model, version_model in rows:
            if rule_model.id in seen:
                continue
            seen.add(rule_model.id)
            results.append(
                RecurringRuleListProjection(
                    rule_id=rule_model.id,
                    organization_id=rule_model.organization_id,
                    name=version_model.name,
                    direction=RecurringDirection.parse(version_model.direction),
                    amount=str(version_model.amount),
                    currency=version_model.currency,
                    status=RecurringRuleStatus.parse(rule_model.status),
                    source_type=RecurringSourceType.parse(rule_model.source_type),
                    frequency=version_model.frequency,
                    interval=version_model.interval,
                    version=rule_model.version,
                )
            )
        return results

    def list_aggregates(
        self,
        organization_id: UUID,
        filters: RecurringRuleFilters,
    ) -> list[RecurringAggregate]:
        stmt = (
            select(RecurringRuleModel)
            .where(RecurringRuleModel.organization_id == organization_id)
            .options(
                selectinload(RecurringRuleModel.versions),
                selectinload(RecurringRuleModel.pauses),
                selectinload(RecurringRuleModel.exceptions),
            )
        )
        if filters.status is not None:
            stmt = stmt.where(RecurringRuleModel.status == filters.status.value)
        elif not filters.include_archived:
            stmt = stmt.where(
                RecurringRuleModel.status != RecurringRuleStatus.ARCHIVED.value
            )
        if filters.source_type is not None:
            stmt = stmt.where(RecurringRuleModel.source_type == filters.source_type.value)
        stmt = stmt.order_by(RecurringRuleModel.updated_at.desc())
        models = list(self.session.scalars(stmt).unique())
        aggregates = [self._mapper.to_entity(model) for model in models]
        if filters.direction is None and filters.currency is None and filters.account_id is None:
            return aggregates
        filtered: list[RecurringAggregate] = []
        for aggregate in aggregates:
            current = next(
                (
                    version
                    for version in reversed(aggregate.versions_tuple())
                    if version.effective_until is None
                ),
                None,
            )
            if current is None:
                continue
            if filters.direction is not None and current.direction != filters.direction:
                continue
            if filters.currency is not None and current.currency != filters.currency:
                continue
            if filters.account_id is not None and current.account_id != filters.account_id:
                continue
            filtered.append(aggregate)
        return filtered
