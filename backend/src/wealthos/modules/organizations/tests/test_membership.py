"""Membership domain tests."""

from uuid import uuid4

import pytest

from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.exceptions import InvalidOrganizationRole
from wealthos.modules.organizations.domain.value_objects.organization_role import (
    OrganizationRole,
)


def test_role_accepts_allowed_values() -> None:
    assert OrganizationRole("owner").value == "owner"
    assert OrganizationRole("MEMBER").value == "member"


def test_role_rejects_invalid() -> None:
    with pytest.raises(InvalidOrganizationRole):
        OrganizationRole("superuser")


def test_membership_starts_active() -> None:
    membership = OrganizationMembership.create(
        organization_id=uuid4(),
        user_id=uuid4(),
        role="member",
    )
    assert membership.status.value == "active"
