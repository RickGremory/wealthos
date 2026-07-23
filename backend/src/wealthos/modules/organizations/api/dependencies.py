"""FastAPI dependencies for the organizations module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.infrastructure.repositories import SqlAlchemyUserRepository
from wealthos.modules.organizations.application.commands.add_organization_member import (
    AddOrganizationMemberCommand,
)
from wealthos.modules.organizations.application.commands.create_organization import (
    CreateOrganizationCommand,
)
from wealthos.modules.organizations.application.queries.list_organization_members import (
    ListOrganizationMembersQuery,
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


def get_organization_repository(
    session: Annotated[Session, Depends(get_db)],
) -> OrganizationRepository:
    return SqlAlchemyOrganizationRepository(session)


def get_membership_repository(
    session: Annotated[Session, Depends(get_db)],
) -> MembershipRepository:
    return SqlAlchemyMembershipRepository(session)


def get_user_repository(
    session: Annotated[Session, Depends(get_db)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_create_organization_command(
    repository: Annotated[OrganizationRepository, Depends(get_organization_repository)],
) -> CreateOrganizationCommand:
    return CreateOrganizationCommand(repository)


def get_add_organization_member_command(
    organizations: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    memberships: Annotated[MembershipRepository, Depends(get_membership_repository)],
) -> AddOrganizationMemberCommand:
    return AddOrganizationMemberCommand(
        organizations=organizations,
        users=users,
        memberships=memberships,
    )


def get_list_organization_members_query(
    organizations: Annotated[OrganizationRepository, Depends(get_organization_repository)],
    memberships: Annotated[MembershipRepository, Depends(get_membership_repository)],
) -> ListOrganizationMembersQuery:
    return ListOrganizationMembersQuery(
        organizations=organizations,
        memberships=memberships,
    )
