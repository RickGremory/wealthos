"""Map OrganizationModel ↔ Organization entity / snapshot."""

from __future__ import annotations

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationSnapshot,
)
from wealthos.modules.organizations.domain.value_objects.currency import Currency
from wealthos.modules.organizations.domain.value_objects.locale import Locale
from wealthos.modules.organizations.domain.value_objects.name import Name
from wealthos.modules.organizations.domain.value_objects.slug import Slug
from wealthos.modules.organizations.domain.value_objects.timezone import Timezone
from wealthos.modules.organizations.infrastructure.models.organization_model import (
    OrganizationModel,
)
from wealthos.shared.base import BaseMapper


class OrganizationMapper(BaseMapper[OrganizationModel, Organization]):
    """Convert between the SQLAlchemy model and the domain aggregate."""

    def to_entity(self, model: OrganizationModel) -> Organization:
        return Organization(
            name=Name(model.name),
            slug=Slug(model.slug),
            currency=Currency(model.currency),
            timezone=Timezone(model.timezone),
            locale=Locale(model.locale),
        )

    def to_model(self, entity: Organization) -> OrganizationModel:
        return OrganizationModel(
            name=entity.name.value,
            slug=entity.slug.value,
            currency=entity.currency.value,
            timezone=entity.timezone.value,
            locale=entity.locale.value,
        )

    def to_snapshot(self, model: OrganizationModel) -> OrganizationSnapshot:
        return OrganizationSnapshot(
            id=model.id,
            name=model.name,
            slug=model.slug,
            currency=model.currency,
            timezone=model.timezone,
            locale=model.locale,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
