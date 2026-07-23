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


def test_mapper_round_trip_entity_fields() -> None:
    mapper = OrganizationMapper()
    entity = Organization.create(
        name="Tecnicora",
        slug="tecnicora",
        currency="USD",
        timezone="America/Mexico_City",
        locale="es_MX",
    )

    model = mapper.to_model(entity)
    restored = mapper.to_entity(model)

    assert restored.name.value == "Tecnicora"
    assert restored.slug.value == "tecnicora"
    assert restored.currency.value == "USD"


def test_mapper_to_snapshot_includes_persistence_identity() -> None:
    mapper = OrganizationMapper()
    now = datetime.now(UTC)
    model = OrganizationModel(
        id=uuid4(),
        name="Personal",
        slug="personal",
        currency="MXN",
        timezone="America/Mexico_City",
        locale="es_MX",
        created_at=now,
        updated_at=now,
    )

    snapshot = mapper.to_snapshot(model)

    assert snapshot.id == model.id
    assert snapshot.slug == "personal"
    assert snapshot.created_at == now
