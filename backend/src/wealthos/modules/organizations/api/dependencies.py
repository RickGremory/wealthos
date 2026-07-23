"""FastAPI dependencies for the organizations module."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.organizations.application.commands.create_organization import (
    CreateOrganizationCommand,
)
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)
from wealthos.modules.organizations.infrastructure.repositories import (
    SqlAlchemyOrganizationRepository,
)


def get_organization_repository(
    session: Annotated[Session, Depends(get_db)],
) -> Generator[OrganizationRepository]:
    """Wire the SQLAlchemy repository behind the domain port."""
    yield SqlAlchemyOrganizationRepository(session)


def get_create_organization_command(
    repository: Annotated[OrganizationRepository, Depends(get_organization_repository)],
) -> CreateOrganizationCommand:
    return CreateOrganizationCommand(repository)
