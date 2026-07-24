"""FastAPI dependencies for the identity module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.categories.application.services.category_seed_service import (
    CategorySeedService,
)
from wealthos.modules.categories.infrastructure.repositories import (
    SqlAlchemyCategoryRepository,
)
from wealthos.modules.identity.application.commands.login_user import LoginUserCommand
from wealthos.modules.identity.application.commands.register_user import RegisterUserCommand
from wealthos.modules.identity.application.services.access_token_service import (
    AccessTokenService,
)
from wealthos.modules.identity.application.services.password_hasher import PasswordHasher
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.infrastructure.repositories import SqlAlchemyUserRepository
from wealthos.modules.identity.infrastructure.security.jwt_access_token_service import (
    JwtAccessTokenService,
)
from wealthos.modules.identity.infrastructure.security.pwdlib_password_hasher import (
    PwdlibPasswordHasher,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    MembershipRepository,
)
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)
from wealthos.modules.organizations.infrastructure.repositories import (
    SqlAlchemyMembershipRepository,
    SqlAlchemyOrganizationRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_user_repository(
    session: Annotated[Session, Depends(get_db)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_password_hasher() -> PasswordHasher:
    return PwdlibPasswordHasher()


def get_access_token_service() -> AccessTokenService:
    return JwtAccessTokenService()


def get_register_user_command(
    session: Annotated[Session, Depends(get_db)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[AccessTokenService, Depends(get_access_token_service)],
) -> RegisterUserCommand:
    users: UserRepository = SqlAlchemyUserRepository(session)
    organizations: OrganizationRepository = SqlAlchemyOrganizationRepository(session)
    memberships: MembershipRepository = SqlAlchemyMembershipRepository(session)
    category_seed = CategorySeedService(SqlAlchemyCategoryRepository(session))
    return RegisterUserCommand(
        users=users,
        organizations=organizations,
        memberships=memberships,
        category_seed=category_seed,
        password_hasher=password_hasher,
        token_service=token_service,
    )


def get_login_user_command(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_service: Annotated[AccessTokenService, Depends(get_access_token_service)],
) -> LoginUserCommand:
    return LoginUserCommand(
        users=users,
        password_hasher=password_hasher,
        token_service=token_service,
    )
