"""Seed default categories for a new organization."""

from __future__ import annotations

from uuid import UUID

from wealthos.modules.categories.domain.entities.category import Category
from wealthos.modules.categories.domain.repositories.category_repository import (
    CategoryRepository,
)

DEFAULT_INCOME = (
    "Honorarios",
    "Ventas",
    "Intereses",
    "Reembolsos",
    "Otros ingresos",
)

DEFAULT_EXPENSE = (
    "Vivienda",
    "Alimentación",
    "Transporte",
    "Salud",
    "Educación",
    "Entretenimiento",
    "Suscripciones",
    "Impuestos",
    "Comisiones",
    "Otros gastos",
)


class CategorySeedService:
    """Create the default system category catalog for an organization."""

    def __init__(self, repository: CategoryRepository) -> None:
        self._repository = repository

    def seed_defaults(self, organization_id: UUID) -> list[Category]:
        categories: list[Category] = [
            Category.create(
                organization_id=organization_id,
                name=name,
                category_type="income",
                is_system=True,
            )
            for name in DEFAULT_INCOME
        ]
        categories.extend(
            Category.create(
                organization_id=organization_id,
                name=name,
                category_type="expense",
                is_system=True,
            )
            for name in DEFAULT_EXPENSE
        )
        return self._repository.add_many(categories)
