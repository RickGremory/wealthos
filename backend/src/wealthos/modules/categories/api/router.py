"""HTTP routes for categories nested under organizations."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from wealthos.core.security.organization_access import OrganizationMember
from wealthos.core.security.organization_permissions import require_organization_role
from wealthos.modules.categories.api.dependencies import (
    get_archive_category_command,
    get_create_category_command,
    get_get_category_query,
    get_list_categories_query,
    get_unit_of_work,
    get_update_category_command,
)
from wealthos.modules.categories.application.commands.archive_category import (
    ArchiveCategoryCommand,
    ArchiveCategoryInput,
)
from wealthos.modules.categories.application.commands.create_category import (
    CreateCategoryCommand,
    CreateCategoryInput,
)
from wealthos.modules.categories.application.commands.update_category import (
    UpdateCategoryCommand,
    UpdateCategoryInput,
)
from wealthos.modules.categories.application.queries.get_category import GetCategoryQuery
from wealthos.modules.categories.application.queries.list_categories import (
    ListCategoriesQuery,
)
from wealthos.modules.categories.domain.exceptions import (
    CategoryAlreadyArchived,
    CategoryDepthExceeded,
    CategoryError,
    CategoryHasActiveChildren,
    CategoryNameEmpty,
    CategoryNameTooLong,
    CategoryNotFoundError,
    CategoryTypeMismatch,
    DuplicateCategory,
    InvalidCategoryType,
    ParentCategoryInactive,
    ParentCategoryNotFound,
    SystemCategoryCannotBeArchived,
)
from wealthos.modules.categories.schemas.collection import (
    CategoryListResponse,
    CategoryTreeResponse,
)
from wealthos.modules.categories.schemas.create import CategoryCreate
from wealthos.modules.categories.schemas.response import (
    CategoryResponse,
    CategoryTreeItem,
)
from wealthos.modules.categories.schemas.update import CategoryUpdate
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork

router = APIRouter()

RequireCreator = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin", "member")),
]
RequireEditor = Annotated[
    OrganizationMembership,
    Depends(require_organization_role("owner", "admin")),
]


@router.post(
    "/{organization_id}/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
)
def create_category(
    organization_id: UUID,
    payload: CategoryCreate,
    _membership: RequireCreator,
    command: Annotated[CreateCategoryCommand, Depends(get_create_category_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CategoryResponse:
    try:
        with uow:
            category = command.execute(
                CreateCategoryInput(
                    organization_id=organization_id,
                    name=payload.name,
                    category_type=payload.category_type,
                    parent_id=payload.parent_id,
                    icon=payload.icon,
                    color=payload.color,
                )
            )
            uow.commit()
    except ParentCategoryNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (
        CategoryNameEmpty,
        CategoryNameTooLong,
        InvalidCategoryType,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except (
        CategoryDepthExceeded,
        CategoryTypeMismatch,
        DuplicateCategory,
        ParentCategoryInactive,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CategoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CategoryResponse.from_entity(category)


@router.get(
    "/{organization_id}/categories",
    summary="List categories",
)
def list_categories(
    organization_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[ListCategoriesQuery, Depends(get_list_categories_query)],
    category_type: Annotated[
        str | None,
        Query(alias="type", pattern="^(income|expense)$"),
    ] = None,
    include_archived: bool = Query(default=False),
    tree: bool = Query(default=False),
) -> CategoryListResponse | CategoryTreeResponse:
    result = query.execute(
        organization_id,
        category_type=category_type,
        include_archived=include_archived,
        as_tree=tree,
    )
    if tree:
        items = [CategoryTreeItem.from_node(node) for node in result]  # type: ignore[arg-type]
        total = sum(1 + len(node.children) for node in result)  # type: ignore[union-attr]
        return CategoryTreeResponse(items=items, total=total)

    items_flat = [CategoryResponse.from_entity(category) for category in result]  # type: ignore[arg-type]
    return CategoryListResponse(items=items_flat, total=len(items_flat))


@router.get(
    "/{organization_id}/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Get category",
)
def get_category(
    organization_id: UUID,
    category_id: UUID,
    _membership: OrganizationMember,
    query: Annotated[GetCategoryQuery, Depends(get_get_category_query)],
) -> CategoryResponse:
    try:
        category = query.execute(organization_id, category_id)
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return CategoryResponse.from_entity(category)


@router.patch(
    "/{organization_id}/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update category",
)
def update_category(
    organization_id: UUID,
    category_id: UUID,
    payload: CategoryUpdate,
    _membership: RequireEditor,
    command: Annotated[UpdateCategoryCommand, Depends(get_update_category_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CategoryResponse:
    try:
        with uow:
            category = command.execute(
                UpdateCategoryInput(
                    organization_id=organization_id,
                    category_id=category_id,
                    name=payload.name,
                    icon=payload.icon,
                    color=payload.color,
                    fields_set=frozenset(payload.model_fields_set),
                )
            )
            uow.commit()
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (CategoryNameEmpty, CategoryNameTooLong) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except DuplicateCategory as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CategoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CategoryResponse.from_entity(category)


@router.post(
    "/{organization_id}/categories/{category_id}/archive",
    response_model=CategoryResponse,
    summary="Archive category",
)
def archive_category(
    organization_id: UUID,
    category_id: UUID,
    _membership: RequireEditor,
    command: Annotated[ArchiveCategoryCommand, Depends(get_archive_category_command)],
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_unit_of_work)],
) -> CategoryResponse:
    try:
        with uow:
            category = command.execute(
                ArchiveCategoryInput(
                    organization_id=organization_id,
                    category_id=category_id,
                )
            )
            uow.commit()
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CategoryAlreadyArchived as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (SystemCategoryCannotBeArchived, CategoryHasActiveChildren) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CategoryError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CategoryResponse.from_entity(category)
