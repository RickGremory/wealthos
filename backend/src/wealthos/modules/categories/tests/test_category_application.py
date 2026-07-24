"""Category application tests with in-memory repository."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

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
from wealthos.modules.categories.application.queries.list_categories import (
    ListCategoriesQuery,
)
from wealthos.modules.categories.application.services.category_seed_service import (
    CategorySeedService,
)
from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.exceptions import (
    CategoryDepthExceeded,
    CategoryHasActiveChildren,
    CategoryTypeMismatch,
    DuplicateCategory,
    ParentCategoryNotFound,
    SystemCategoryCannotBeArchived,
)
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType


class InMemoryCategoryRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[UUID, UUID], Category] = {}

    def add(self, category: Category) -> Category:
        self._items[(category.organization_id, category.id)] = category
        return category

    def add_many(self, categories: list[Category]) -> list[Category]:
        for category in categories:
            self.add(category)
        return categories

    def get_by_id(self, organization_id: UUID, category_id: UUID) -> Category | None:
        return self._items.get((organization_id, category_id))

    def exists_by_normalized_name(
        self,
        organization_id: UUID,
        category_type: CategoryType,
        normalized_name: str,
        parent_id: UUID | None,
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        for category in self._items.values():
            if exclude_id is not None and category.id == exclude_id:
                continue
            if (
                category.organization_id == organization_id
                and category.category_type == category_type
                and category.name.normalized == normalized_name
                and category.parent_id == parent_id
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
        categories = [c for (org_id, _), c in self._items.items() if org_id == organization_id]
        if category_type is not None:
            categories = [c for c in categories if c.category_type == category_type]
        if not include_archived:
            categories = [c for c in categories if c.is_active]
        return categories

    def count_active_children(self, organization_id: UUID, category_id: UUID) -> int:
        return sum(
            1
            for category in self._items.values()
            if category.organization_id == organization_id
            and category.parent_id == category_id
            and category.is_active
        )

    def save(self, category: Category) -> Category:
        self._items[(category.organization_id, category.id)] = category
        return category


def test_create_root_and_valid_subcategory() -> None:
    repo = InMemoryCategoryRepository()
    org_id = uuid4()
    root = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Vivienda",
            category_type="expense",
        )
    )
    child = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
            parent_id=root.id,
        )
    )
    assert child.parent_id == root.id


def test_reject_missing_parent_and_cross_org_parent() -> None:
    repo = InMemoryCategoryRepository()
    org_a = uuid4()
    org_b = uuid4()
    parent = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_a,
            name="Vivienda",
            category_type="expense",
        )
    )
    with pytest.raises(ParentCategoryNotFound):
        CreateCategoryCommand(repo).execute(
            CreateCategoryInput(
                organization_id=org_a,
                name="Renta",
                category_type="expense",
                parent_id=uuid4(),
            )
        )
    with pytest.raises(ParentCategoryNotFound):
        CreateCategoryCommand(repo).execute(
            CreateCategoryInput(
                organization_id=org_b,
                name="Renta",
                category_type="expense",
                parent_id=parent.id,
            )
        )


def test_reject_third_level_and_type_mismatch() -> None:
    repo = InMemoryCategoryRepository()
    org_id = uuid4()
    root = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Vivienda",
            category_type="expense",
        )
    )
    child = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
            parent_id=root.id,
        )
    )
    with pytest.raises(CategoryDepthExceeded):
        CreateCategoryCommand(repo).execute(
            CreateCategoryInput(
                organization_id=org_id,
                name="Agua",
                category_type="expense",
                parent_id=child.id,
            )
        )
    with pytest.raises(CategoryTypeMismatch):
        CreateCategoryCommand(repo).execute(
            CreateCategoryInput(
                organization_id=org_id,
                name="Renta recibida",
                category_type="income",
                parent_id=root.id,
            )
        )


def test_duplicate_rules_same_level_and_different_levels() -> None:
    repo = InMemoryCategoryRepository()
    org_id = uuid4()
    root = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Vivienda",
            category_type="expense",
        )
    )
    CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
            parent_id=root.id,
        )
    )
    with pytest.raises(DuplicateCategory):
        CreateCategoryCommand(repo).execute(
            CreateCategoryInput(
                organization_id=org_id,
                name="renta",
                category_type="expense",
                parent_id=root.id,
            )
        )
    # Same display name allowed at a different level.
    CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
        )
    )
    # Same name allowed for income vs expense.
    CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Intereses",
            category_type="income",
        )
    )
    CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Intereses",
            category_type="expense",
        )
    )


def test_list_flat_and_tree() -> None:
    repo = InMemoryCategoryRepository()
    org_id = uuid4()
    root = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Vivienda",
            category_type="expense",
        )
    )
    CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
            parent_id=root.id,
        )
    )
    CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Honorarios",
            category_type="income",
        )
    )

    flat = ListCategoriesQuery(repo).execute(org_id, category_type="expense")
    assert len(flat) == 2

    tree = ListCategoriesQuery(repo).execute(org_id, category_type="expense", as_tree=True)
    assert len(tree) == 1
    assert tree[0].category.name.value == "Vivienda"
    assert len(tree[0].children) == 1
    assert tree[0].children[0].category.name.value == "Renta"


def test_archive_rules() -> None:
    repo = InMemoryCategoryRepository()
    org_id = uuid4()
    root = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Oficina",
            category_type="expense",
        )
    )
    child = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
            parent_id=root.id,
        )
    )
    with pytest.raises(CategoryHasActiveChildren):
        ArchiveCategoryCommand(repo).execute(
            ArchiveCategoryInput(organization_id=org_id, category_id=root.id)
        )

    ArchiveCategoryCommand(repo).execute(
        ArchiveCategoryInput(organization_id=org_id, category_id=child.id)
    )
    archived_parent = ArchiveCategoryCommand(repo).execute(
        ArchiveCategoryInput(organization_id=org_id, category_id=root.id)
    )
    assert archived_parent.is_active is False

    system = Category.create(
        organization_id=org_id,
        name="Vivienda",
        category_type="expense",
        is_system=True,
    )
    repo.add(system)
    with pytest.raises(SystemCategoryCannotBeArchived):
        ArchiveCategoryCommand(repo).execute(
            ArchiveCategoryInput(organization_id=org_id, category_id=system.id)
        )


def test_update_rename_and_seed_defaults() -> None:
    repo = InMemoryCategoryRepository()
    org_id = uuid4()
    category = CreateCategoryCommand(repo).execute(
        CreateCategoryInput(
            organization_id=org_id,
            name="Renta",
            category_type="expense",
        )
    )
    updated = UpdateCategoryCommand(repo).execute(
        UpdateCategoryInput(
            organization_id=org_id,
            category_id=category.id,
            name="Renta mensual",
            fields_set=frozenset({"name"}),
        )
    )
    assert updated.name.value == "Renta mensual"

    seeded = CategorySeedService(repo).seed_defaults(uuid4())
    assert len(seeded) == 20
    assert all(item.is_system for item in seeded)
