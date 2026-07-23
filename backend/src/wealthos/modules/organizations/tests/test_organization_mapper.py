"""Mapper unit tests."""

from datetime import UTC, datetime
from uuid import uuid4

from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.infrastructure.mappers.organization_mapper import (
    OrganizationMapper,
)
from wealthos.modules.organizations.infrastructure.models.organization_model import (
    OrganizationModel,
)


def test_mapper_round_trip_preserves_identity_and_fields() -> None:
    mapper = OrganizationMapper()
    entity = Organization.create(
        name="Tecnicora",
        slug="tecnicora",
        currency="USD",
        timezone="America/Cancun",
        locale="es-MX",
    )

    model = mapper.to_model(entity)
    restored = mapper.to_entity(model)

    assert restored.id == entity.id
    assert restored.name.value == "Tecnicora"
    assert restored.slug.value == "tecnicora"
    assert restored.currency.value == "USD"
    assert restored.locale.value == "es-MX"


def test_mapper_to_entity_from_persisted_model() -> None:
    mapper = OrganizationMapper()
    now = datetime.now(UTC)
    model_id = uuid4()
    model = OrganizationModel(
        id=model_id,
        name="Personal",
        slug="personal",
        currency="MXN",
        timezone="America/Cancun",
        locale="es-MX",
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )

    entity = mapper.to_entity(model)

    assert entity.id == model_id
    assert entity.slug.value == "personal"
    assert entity.created_at == now
