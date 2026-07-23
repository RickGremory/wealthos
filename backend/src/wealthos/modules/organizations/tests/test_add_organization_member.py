"""AddOrganizationMember application tests."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import UserNotFoundError
from wealthos.modules.identity.domain.value_objects.email import Email
from wealthos.modules.organizations.application.commands.add_organization_member import (
    AddOrganizationMemberCommand,
    AddOrganizationMemberInput,
)
from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.exceptions import (
    OrganizationMemberAlreadyExists,
    OrganizationNotFoundError,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    OrganizationMemberView,
)
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug


class InMemoryOrganizationRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Organization] = {}

    def add(self, organization: Organization) -> Organization:
        self._by_id[organization.id] = organization
        return organization

    def get_by_id(self, organization_id: UUID) -> Organization | None:
        return self._by_id.get(organization_id)

    def get_by_slug(self, slug: OrganizationSlug) -> Organization | None:
        for org in self._by_id.values():
            if org.slug == slug:
                return org
        return None


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}

    def add(self, user: User) -> User:
        self._by_id[user.id] = user
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)

    def get_by_email(self, email: Email) -> User | None:
        for user in self._by_id.values():
            if user.email == email:
                return user
        return None


class InMemoryMembershipRepository:
    def __init__(self) -> None:
        self._items: list[OrganizationMembership] = []

    def add(self, membership: OrganizationMembership) -> OrganizationMembership:
        self._items.append(membership)
        return membership

    def get_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMembership | None:
        for item in self._items:
            if item.organization_id == organization_id and item.user_id == user_id:
                return item
        return None

    def list_by_organization(self, organization_id: UUID) -> list[OrganizationMemberView]:
        return []


def _command() -> tuple[
    AddOrganizationMemberCommand,
    InMemoryOrganizationRepository,
    InMemoryUserRepository,
    InMemoryMembershipRepository,
]:
    orgs = InMemoryOrganizationRepository()
    users = InMemoryUserRepository()
    memberships = InMemoryMembershipRepository()
    return (
        AddOrganizationMemberCommand(
            organizations=orgs,
            users=users,
            memberships=memberships,
        ),
        orgs,
        users,
        memberships,
    )


def test_add_member() -> None:
    command, orgs, users, _ = _command()
    org = Organization.create(name="Personal", slug="personal")
    user = User.create(email="a@example.com", display_name="Ada")
    orgs.add(org)
    users.add(user)

    membership = command.execute(
        AddOrganizationMemberInput(
            organization_id=org.id,
            user_id=user.id,
            role="member",
        )
    )
    assert membership.role.value == "member"
    assert membership.status.value == "active"


def test_add_member_rejects_missing_user() -> None:
    command, orgs, _, _ = _command()
    org = Organization.create(name="Personal", slug="personal")
    orgs.add(org)

    with pytest.raises(UserNotFoundError):
        command.execute(
            AddOrganizationMemberInput(
                organization_id=org.id,
                user_id=uuid4(),
                role="member",
            )
        )


def test_add_member_rejects_missing_organization() -> None:
    command, _, users, _ = _command()
    user = User.create(email="a@example.com", display_name="Ada")
    users.add(user)

    with pytest.raises(OrganizationNotFoundError):
        command.execute(
            AddOrganizationMemberInput(
                organization_id=uuid4(),
                user_id=user.id,
                role="member",
            )
        )


def test_add_member_rejects_duplicate() -> None:
    command, orgs, users, _ = _command()
    org = Organization.create(name="Personal", slug="personal")
    user = User.create(email="a@example.com", display_name="Ada")
    orgs.add(org)
    users.add(user)
    payload = AddOrganizationMemberInput(
        organization_id=org.id,
        user_id=user.id,
        role="member",
    )
    command.execute(payload)
    with pytest.raises(OrganizationMemberAlreadyExists):
        command.execute(payload)
