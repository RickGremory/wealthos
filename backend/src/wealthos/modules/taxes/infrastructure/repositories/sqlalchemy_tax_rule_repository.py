"""SQLAlchemy TaxRuleRepository."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.infrastructure.mappers.tax_rule_mapper import TaxRuleMapper
from wealthos.modules.taxes.infrastructure.models.tax_models import (
    TaxRuleCategoryModel,
    TaxRuleModel,
)
from wealthos.shared.base import BaseRepository


class SqlAlchemyTaxRuleRepository(BaseRepository[TaxRuleModel]):
    def __init__(self, session: Session, mapper: TaxRuleMapper | None = None) -> None:
        super().__init__(session, TaxRuleModel)
        self._mapper = mapper or TaxRuleMapper()

    def add(self, rule: TaxRule) -> TaxRule:
        model = self._mapper.to_model(rule)
        super().add(model)
        self._replace_categories(rule.id, rule.category_ids)
        self.flush()
        self.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, organization_id: UUID, rule_id: UUID) -> TaxRule | None:
        stmt = select(TaxRuleModel).where(
            TaxRuleModel.organization_id == organization_id,
            TaxRuleModel.id == rule_id,
        )
        model = self.session.scalars(stmt).first()
        return self._to_entity(model) if model else None

    def list_by_profile(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[TaxRule]:
        stmt = select(TaxRuleModel).where(
            TaxRuleModel.organization_id == organization_id,
            TaxRuleModel.tax_profile_id == tax_profile_id,
        )
        if not include_archived:
            stmt = stmt.where(TaxRuleModel.archived_at.is_(None))
        stmt = stmt.order_by(TaxRuleModel.priority.asc(), TaxRuleModel.created_at.asc())
        return [self._to_entity(model) for model in self.session.scalars(stmt)]

    def list_active_for_period(
        self,
        organization_id: UUID,
        tax_profile_id: UUID,
        period_from: date,
        period_to: date,
    ) -> list[TaxRule]:
        stmt = select(TaxRuleModel).where(
            TaxRuleModel.organization_id == organization_id,
            TaxRuleModel.tax_profile_id == tax_profile_id,
            TaxRuleModel.is_active.is_(True),
            TaxRuleModel.archived_at.is_(None),
            TaxRuleModel.effective_from <= period_to,
        )
        stmt = stmt.where(
            (TaxRuleModel.effective_to.is_(None)) | (TaxRuleModel.effective_to >= period_from)
        )
        stmt = stmt.order_by(TaxRuleModel.priority.asc())
        return [self._to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, rule: TaxRule) -> TaxRule:
        model = self.session.get(TaxRuleModel, rule.id)
        if model is None or model.organization_id != rule.organization_id:
            raise LookupError("Tax rule not found for save.")
        self._mapper.apply_to_model(rule, model)
        self._replace_categories(rule.id, rule.category_ids)
        self.flush()
        self.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: TaxRuleModel) -> TaxRule:
        category_ids = self._load_category_ids(model.id)
        return self._mapper.to_entity(model, category_ids=category_ids)

    def _load_category_ids(self, rule_id: UUID) -> tuple[UUID, ...]:
        stmt = select(TaxRuleCategoryModel.category_id).where(
            TaxRuleCategoryModel.tax_rule_id == rule_id
        )
        return tuple(self.session.scalars(stmt).all())

    def _replace_categories(
        self,
        rule_id: UUID,
        category_ids: tuple[UUID, ...] | list[UUID],
    ) -> None:
        self.session.execute(
            delete(TaxRuleCategoryModel).where(TaxRuleCategoryModel.tax_rule_id == rule_id)
        )
        for category_id in category_ids:
            self.session.add(TaxRuleCategoryModel(tax_rule_id=rule_id, category_id=category_id))
