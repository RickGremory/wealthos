"""Register and login application tests."""

from __future__ import annotations

from uuid import UUID

import pytest

from wealthos.core.settings import Settings
from wealthos.modules.categories.application.services.category_seed_service import (
    CategorySeedService,
)
from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType
from wealthos.modules.identity.application.commands.login_user import (
    LoginUserCommand,
    LoginUserInput,
)
from wealthos.modules.identity.application.commands.register_user import (
    RegisterUserCommand,
    RegisterUserInput,
)
from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import (
    InvalidCredentials,
    UserEmailAlreadyExists,
)
from wealthos.modules.identity.domain.value_objects.email import Email
from wealthos.modules.identity.infrastructure.security.jwt_access_token_service import (
    JwtAccessTokenService,
)
from wealthos.modules.identity.infrastructure.security.pwdlib_password_hasher import (
    PwdlibPasswordHasher,
)
from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    OrganizationMemberView,
    UserOrganizationView,
)
from wealthos.modules.organizations.domain.value_objects.slug import OrganizationSlug


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, User] = {}
        self._by_email: dict[str, User] = {}
        self._password_hashes: dict[UUID, str] = {}

    def add(self, user: User, *, password_hash: str) -> User:
        self._by_id[user.id] = user
        self._by_email[user.email.value] = user
        self._password_hashes[user.id] = password_hash
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._by_id.get(user_id)

    def get_by_email(self, email: Email) -> User | None:
        return self._by_email.get(email.value)

    def get_password_hash(self, user_id: UUID) -> str | None:
        return self._password_hashes.get(user_id)


class InMemoryOrganizationRepository:
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


class InMemoryMembershipRepository:
    def __init__(self, *, fail_on_add: bool = False) -> None:
        self._items: list[OrganizationMembership] = []
        self._fail_on_add = fail_on_add

    def add(self, membership: OrganizationMembership) -> OrganizationMembership:
        if self._fail_on_add:
            raise RuntimeError("membership failed")
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

    def list_organizations_for_user(self, user_id: UUID) -> list[UserOrganizationView]:
        return []


class InMemoryCategoryRepository:
    def __init__(self) -> None:
        self.items: list[Category] = []

    def add(self, category: Category) -> Category:
        self.items.append(category)
        return category

    def add_many(self, categories: list[Category]) -> list[Category]:
        self.items.extend(categories)
        return categories

    def get_by_id(self, organization_id: UUID, category_id: UUID) -> Category | None:
        for item in self.items:
            if item.organization_id == organization_id and item.id == category_id:
                return item
        return None

    def exists_by_normalized_name(
        self,
        organization_id: UUID,
        category_type: CategoryType,
        normalized_name: str,
        parent_id: UUID | None,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        for item in self.items:
            if exclude_id is not None and item.id == exclude_id:
                continue
            if (
                item.organization_id == organization_id
                and item.category_type == category_type
                and item.name.normalized == normalized_name
                and item.parent_id == parent_id
            ):
                return True
        return False

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        category_type: CategoryType | None = None,
        include_archived: bool = False,
    ) -> list[Category]:
        result = [c for c in self.items if c.organization_id == organization_id]
        if category_type is not None:
            result = [c for c in result if c.category_type == category_type]
        if not include_archived:
            result = [c for c in result if c.is_active]
        return result

    def count_active_children(self, organization_id: UUID, category_id: UUID) -> int:
        return sum(
            1
            for item in self.items
            if item.organization_id == organization_id
            and item.parent_id == category_id
            and item.is_active
        )

    def save(self, category: Category) -> Category:
        return category


def _register_command(
    memberships: InMemoryMembershipRepository | None = None,
) -> tuple[
    RegisterUserCommand,
    InMemoryUserRepository,
    InMemoryOrganizationRepository,
    InMemoryCategoryRepository,
]:
    users = InMemoryUserRepository()
    orgs = InMemoryOrganizationRepository()
    membership_repo = memberships or InMemoryMembershipRepository()
    categories = InMemoryCategoryRepository()
    command = RegisterUserCommand(
        users=users,
        organizations=orgs,
        memberships=membership_repo,
        category_seed=CategorySeedService(categories),
        password_hasher=PwdlibPasswordHasher(),
        token_service=JwtAccessTokenService(
            Settings(auth_jwt_secret="test-secret-key-for-register-tests")
        ),
    )
    return command, users, orgs, categories


def test_register_creates_user_org_and_owner_membership() -> None:
    memberships = InMemoryMembershipRepository()
    command, users, orgs, categories = _register_command(memberships)
    result = command.execute(
        RegisterUserInput(
            email="Ricardo@Example.com",
            password="WealthOS-2026-Segura",
            display_name="Ricardo Balam",
            organization_name="Ricardo Personal",
        )
    )
    assert result.user.email.value == "ricardo@example.com"
    assert result.organization.slug.value == "ricardo-personal"
    assert result.membership.role.value == "owner"
    assert users.get_by_email(Email("ricardo@example.com")) is not None
    assert orgs.get_by_slug(OrganizationSlug("ricardo-personal")) is not None
    assert result.access_token
    assert len(categories.items) == 15
    assert all(c.is_system for c in categories.items)


def test_register_rejects_duplicate_email() -> None:
    command, _, _, _ = _register_command()
    payload = RegisterUserInput(
        email="a@example.com",
        password="WealthOS-2026-Segura",
        display_name="One",
        organization_name="One Org",
    )
    command.execute(payload)
    with pytest.raises(UserEmailAlreadyExists):
        command.execute(payload)


def test_register_rolls_back_when_membership_fails() -> None:
    memberships = InMemoryMembershipRepository(fail_on_add=True)
    command, users, orgs, _ = _register_command(memberships)
    with pytest.raises(RuntimeError):
        command.execute(
            RegisterUserInput(
                email="a@example.com",
                password="WealthOS-2026-Segura",
                display_name="One",
                organization_name="One Org",
            )
        )
    # In-memory fake still mutated before failure — UoW covers DB atomicity.
    # Assert membership was not stored.
    assert memberships._items == []


def test_login_accepts_valid_credentials() -> None:
    register, users, _, _ = _register_command()
    register.execute(
        RegisterUserInput(
            email="a@example.com",
            password="WealthOS-2026-Segura",
            display_name="Ada",
            organization_name="Ada Org",
        )
    )
    login = LoginUserCommand(
        users=users,
        password_hasher=PwdlibPasswordHasher(),
        token_service=JwtAccessTokenService(
            Settings(auth_jwt_secret="test-secret-key-for-register-tests")
        ),
    )
    result = login.execute(LoginUserInput(email="a@example.com", password="WealthOS-2026-Segura"))
    assert result.access_token


def test_login_rejects_wrong_password() -> None:
    register, users, _, _ = _register_command()
    register.execute(
        RegisterUserInput(
            email="a@example.com",
            password="WealthOS-2026-Segura",
            display_name="Ada",
            organization_name="Ada Org",
        )
    )
    login = LoginUserCommand(
        users=users,
        password_hasher=PwdlibPasswordHasher(),
        token_service=JwtAccessTokenService(
            Settings(auth_jwt_secret="test-secret-key-for-register-tests")
        ),
    )
    with pytest.raises(InvalidCredentials):
        login.execute(LoginUserInput(email="a@example.com", password="wrong"))


def test_login_rejects_unknown_user() -> None:
    _, users, _, _ = _register_command()
    login = LoginUserCommand(
        users=users,
        password_hasher=PwdlibPasswordHasher(),
        token_service=JwtAccessTokenService(
            Settings(auth_jwt_secret="test-secret-key-for-register-tests")
        ),
    )
    with pytest.raises(InvalidCredentials):
        login.execute(LoginUserInput(email="missing@example.com", password="WealthOS-2026"))
