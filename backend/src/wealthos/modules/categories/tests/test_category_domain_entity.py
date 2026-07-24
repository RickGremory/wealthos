"""Domain entity tests for Category."""

from __future__ import annotations

from uuid import uuid4

import pytest

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.exceptions import (
    CategoryAlreadyArchived,
    SystemCategoryCannotBeArchived,
)


def test_create_root_and_subcategory() -> None:
    org_id = uuid4()
    root = Category.create(
        organization_id=org_id,
        name="Vivienda",
        category_type="expense",
    )
    child = Category.create(
        organization_id=org_id,
        name="Renta",
        category_type="expense",
        parent_id=root.id,
    )
    assert root.parent_id is None
    assert child.parent_id == root.id
    assert root.is_active is True


def test_rename_category() -> None:
    category = Category.create(
        organization_id=uuid4(),
        name="Renta",
        category_type="expense",
    )
    category.rename("Renta mensual")
    assert category.name.value == "Renta mensual"


def test_archive_normal_category() -> None:
    category = Category.create(
        organization_id=uuid4(),
        name="Temporal",
        category_type="income",
    )
    category.archive()
    assert category.is_active is False
    assert category.archived_at is not None


def test_reject_archive_system_category() -> None:
    category = Category.create(
        organization_id=uuid4(),
        name="Vivienda",
        category_type="expense",
        is_system=True,
    )
    with pytest.raises(SystemCategoryCannotBeArchived):
        category.archive()


def test_reject_double_archive() -> None:
    category = Category.create(
        organization_id=uuid4(),
        name="Temporal",
        category_type="income",
    )
    category.archive()
    with pytest.raises(CategoryAlreadyArchived):
        category.archive()
