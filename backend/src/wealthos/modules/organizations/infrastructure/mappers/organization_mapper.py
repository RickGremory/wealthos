"""Map Organization ↔ OrganizationModel."""

from __future__ import annotations

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.value_objects.currency import Currency
from wealthos.modules.organizations.domain.value_objects.locale import Locale
from wealthos.modules.organizations.domain.value_objects.name import OrganizationName
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug
from wealthos.modules.organizations.domain.value_objects.timezone import Timezone
from wealthos.modules.organizations.infrastructure.models.organization_model import (
    OrganizationModel,
)
from wealthos.shared.base import BaseMapper


class OrganizationMapper(BaseMapper[OrganizationModel, Organization]):
    """Convert between the SQLAlchemy model and the domain aggregate."""

    def to_entity(self, model: OrganizationModel) -> Organization:
        return Organization(
            id=model.id,
            name=OrganizationName(model.name),
            slug=OrganizationSlug(model.slug),
            currency=Currency(model.currency),
            timezone=Timezone(model.timezone),
            locale=Locale(model.locale),
            created_at=model.created_at,
            updated_at=model.updated_at,
            debt_strategy=model.debt_strategy,
        )

    def to_model(self, entity: Organization) -> OrganizationModel:
        return OrganizationModel(
            id=entity.id,
            name=entity.name.value,
            slug=entity.slug.value,
            currency=entity.currency.value,
            timezone=entity.timezone.value,
            locale=entity.locale.value,
            debt_strategy=entity.debt_strategy,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=None,
        )

    def apply_to_model(self, entity: Organization, model: OrganizationModel) -> OrganizationModel:
        model.name = entity.name.value
        model.slug = entity.slug.value
        model.currency = entity.currency.value
        model.timezone = entity.timezone.value
        model.locale = entity.locale.value
        model.debt_strategy = entity.debt_strategy
        model.updated_at = entity.updated_at
        return model
