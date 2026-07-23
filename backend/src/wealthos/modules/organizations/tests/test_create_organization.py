"""Create-command unit tests with an in-memory repository."""

from __future__ import annotations

from uuid import UUID

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
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug


class InMemoryOrganizationRepository:
    """Fake repository for application-layer tests."""

    def __init__(self) -> None:
        self._by_id: dict[UUID, Organization] = {}
        self._by_slug: dict[str, Organization] = {}

    def add(self, organization: Organization) -> Organization:
        self._by_id[organization.id] = organization
        self._by_slug[organization.slug.value] = organization
        return organization

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        return self._by_id.get(organization_id)

    def get_by_slug(self, slug: OrganizationSlug) -> Organization | None:
        return self._by_slug.get(slug.value)


def test_create_organization_persists_entity() -> None:
    repo = InMemoryOrganizationRepository()
    command = CreateOrganizationCommand(repo)

    organization = command.execute(
        CreateOrganizationInput(name="Ricardo Personal", slug="ricardo-personal")
    )

    assert organization.name.value == "Ricardo Personal"
    assert organization.slug.value == "ricardo-personal"
    assert organization.currency.value == "MXN"
    assert organization.timezone.value == "America/Cancun"
    assert organization.locale.value == "es-MX"
    assert repo.get_by_id(organization.id) is organization


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
