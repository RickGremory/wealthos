"""FastAPI dependencies for the categories module."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.categories.application.commands.archive_category import (
    ArchiveCategoryCommand,
)
from wealthos.modules.categories.application.commands.create_category import (
    CreateCategoryCommand,
)
from wealthos.modules.categories.application.commands.update_category import (
    UpdateCategoryCommand,
)
from wealthos.modules.categories.application.queries.get_category import GetCategoryQuery
from wealthos.modules.categories.application.queries.list_categories import (
    ListCategoriesQuery,
)
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)
from wealthos.modules.categories.infrastructure.repositories import (
    SqlAlchemyCategoryRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_category_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CategoryRepository:
    return SqlAlchemyCategoryRepository(session)


def get_create_category_command(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CreateCategoryCommand:
    return CreateCategoryCommand(repository)


def get_update_category_command(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> UpdateCategoryCommand:
    return UpdateCategoryCommand(repository)


def get_archive_category_command(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> ArchiveCategoryCommand:
    return ArchiveCategoryCommand(repository)


def get_get_category_query(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> GetCategoryQuery:
    return GetCategoryQuery(repository)


def get_list_categories_query(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> ListCategoriesQuery:
    return ListCategoriesQuery(repository)
