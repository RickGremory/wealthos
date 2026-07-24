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
    "Comisiones",
    "Otros gastos",
)

TAX_CATEGORY_TREE: tuple[tuple[str, str], ...] = (
    ("taxes.root", "Impuestos"),
    ("taxes.income_tax", "ISR"),
    ("taxes.value_added_tax", "IVA"),
    ("taxes.withholding", "Retenciones"),
    ("taxes.social_security", "Seguridad social"),
    ("taxes.other", "Otros impuestos"),
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
        tax_root = Category.create(
            organization_id=organization_id,
            name=TAX_CATEGORY_TREE[0][1],
            category_type="expense",
            is_system=True,
            system_code=TAX_CATEGORY_TREE[0][0],
        )
        categories.append(tax_root)
        for system_code, name in TAX_CATEGORY_TREE[1:]:
            categories.append(
                Category.create(
                    organization_id=organization_id,
                    name=name,
                    category_type="expense",
                    parent_id=tax_root.id,
                    is_system=True,
                    system_code=system_code,
                )
            )
        return self._repository.add_many(categories)
