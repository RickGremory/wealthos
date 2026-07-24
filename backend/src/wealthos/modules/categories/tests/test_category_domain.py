"""Domain tests for CategoryName and CategoryType."""

from __future__ import annotations

import pytest

from wealthos.modules.categories.domain.exceptions import (
    CategoryNameEmpty,
    InvalidCategoryType,
)
from wealthos.modules.categories.domain.value_objects.category_name import (
    CategoryName,
    normalize_category_name,
)
from wealthos.modules.categories.domain.value_objects.category_type import CategoryType


def test_category_name_normalizes_spaces_and_preserves_display() -> None:
    name = CategoryName("  Alimentación   Básica  ")
    assert name.value == "Alimentación Básica"
    assert name.normalized == "alimentacion basica"


def test_category_name_strips_accents_for_normalized() -> None:
    assert normalize_category_name("  Alimentación  ") == "alimentacion"
    assert CategoryName("Intereses").normalized == CategoryName("interéses").normalized


def test_category_name_rejects_empty() -> None:
    with pytest.raises(CategoryNameEmpty):
        CategoryName(" ")
    with pytest.raises(CategoryNameEmpty):
        CategoryName("A")


def test_category_type_accepts_income_and_expense() -> None:
    income = CategoryType("income")
    expense = CategoryType("EXPENSE")
    assert income.is_income is True
    assert income.is_expense is False
    assert expense.is_expense is True


def test_category_type_rejects_unknown() -> None:
    with pytest.raises(InvalidCategoryType):
        CategoryType("transfer")
