"""In-memory repository and create-command unit tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from wealthos.modules.organizations.application.commands.create_organization import (
    CreateOrganizationCommand,
    CreateOrganizationInput,
)
from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.exceptions import (
    InvalidCurrency,
    OrganizationSlugAlreadyExists,
)
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationSnapshot,
)
from wealthos.modules.organizations.domain.value_objects.slug import Slug


class InMemoryOrganizationRepository:
    """Fake repository for application-layer tests."""

    def __init__(self) -> None:
        self._by_slug: dict[str, Organization] = {}
        self._snapshots: dict[str, OrganizationSnapshot] = {}

    def add(self, organization: Organization) -> OrganizationSnapshot:
        now = datetime.now(UTC)
        snapshot = OrganizationSnapshot(
            id=uuid4(),
            name=organization.name.value,
            slug=organization.slug.value,
            currency=organization.currency.value,
            timezone=organization.timezone.value,
            locale=organization.locale.value,
            created_at=now,
            updated_at=now,
        )
        self._by_slug[organization.slug.value] = organization
        self._snapshots[organization.slug.value] = snapshot
        return snapshot

    def get_by_slug(self, slug: Slug) -> Organization | None:
        return self._by_slug.get(slug.value)

    def list(self) -> list[Organization]:
        return list(self._by_slug.values())


def test_create_organization_persists_snapshot() -> None:
    repo = InMemoryOrganizationRepository()
    command = CreateOrganizationCommand(repo)

    snapshot = command.execute(
        CreateOrganizationInput(name="Ricardo Personal", slug="ricardo-personal")
    )

    assert snapshot.name == "Ricardo Personal"
    assert snapshot.slug == "ricardo-personal"
    assert snapshot.currency == "MXN"
    assert snapshot.id is not None


def test_create_organization_rejects_duplicate_slug() -> None:
    repo = InMemoryOrganizationRepository()
    command = CreateOrganizationCommand(repo)
    command.execute(CreateOrganizationInput(name="One", slug="shared"))

    with pytest.raises(OrganizationSlugAlreadyExists):
        command.execute(CreateOrganizationInput(name="Two", slug="shared"))


def test_create_organization_rejects_invalid_currency() -> None:
    repo = InMemoryOrganizationRepository()
    command = CreateOrganizationCommand(repo)

    with pytest.raises(InvalidCurrency):
        command.execute(
            CreateOrganizationInput(
                name="Personal",
                slug="personal",
                currency="BTC",
            )
        )
