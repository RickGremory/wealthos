"""FastAPI dependencies for tax_mx."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.categories.infrastructure.repositories import SqlAlchemyCategoryRepository
from wealthos.modules.tax_mx.application.commands.calculate_mexico_tax_period import (
    CalculateMexicoTaxPeriodCommand,
)
from wealthos.modules.tax_mx.application.commands.classify_mexico_tax_transaction import (
    ClassifyMexicoTaxTransactionCommand,
)
from wealthos.modules.tax_mx.application.commands.create_mexico_tax_configuration import (
    CreateMexicoTaxConfigurationCommand,
)
from wealthos.modules.tax_mx.application.commands.map_mexico_tax_category import (
    MapMexicoTaxCategoryCommand,
    UpdateMexicoTaxCategoryMappingCommand,
)
from wealthos.modules.tax_mx.application.commands.revise_mexico_tax_configuration import (
    ReviseMexicoTaxConfigurationCommand,
)
from wealthos.modules.tax_mx.application.queries.mexico_tax_queries import (
    GetMexicoTaxConfigurationQuery,
    GetMexicoTaxSummaryQuery,
    GetMexicoTaxWorkpaperQuery,
    ListMexicoCategoryMappingsQuery,
    ListMexicoTaxCatalogsQuery,
    ListUnclassifiedTaxTransactionsQuery,
)
from wealthos.modules.tax_mx.infrastructure.repositories import (
    SqlAlchemyMexicoTaxCatalogRepository,
    SqlAlchemyMexicoTaxCategoryMappingRepository,
    SqlAlchemyMexicoTaxConfigurationRepository,
    SqlAlchemyMexicoTaxDetailsRepository,
    SqlAlchemyMexicoTaxReadRepository,
    SqlAlchemyMexicoTaxSnapshotRepository,
    SqlAlchemyMexicoTaxTransactionOverrideRepository,
    SqlAlchemyMexicoTaxWithholdingRepository,
    SqlAlchemyTaxEvidenceRepository,
)
from wealthos.modules.taxes.infrastructure.repositories import (
    SqlAlchemyTaxCalculationRepository,
    SqlAlchemyTaxPaymentRepository,
    SqlAlchemyTaxPeriodRepository,
    SqlAlchemyTaxProfileRepository,
    SqlAlchemyTaxReadRepository,
)
from wealthos.modules.transactions.infrastructure.repositories import (
    SqlAlchemyTransactionRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_create_configuration_command(
    session: Annotated[Session, Depends(get_db)],
) -> CreateMexicoTaxConfigurationCommand:
    return CreateMexicoTaxConfigurationCommand(
        SqlAlchemyMexicoTaxConfigurationRepository(session),
        SqlAlchemyTaxProfileRepository(session),
        SqlAlchemyMexicoTaxCatalogRepository(session),
    )


def get_revise_configuration_command(
    session: Annotated[Session, Depends(get_db)],
    create: Annotated[
        CreateMexicoTaxConfigurationCommand, Depends(get_create_configuration_command)
    ],
) -> ReviseMexicoTaxConfigurationCommand:
    return ReviseMexicoTaxConfigurationCommand(
        SqlAlchemyMexicoTaxConfigurationRepository(session),
        create,
    )


def get_map_category_command(
    session: Annotated[Session, Depends(get_db)],
) -> MapMexicoTaxCategoryCommand:
    return MapMexicoTaxCategoryCommand(
        SqlAlchemyMexicoTaxCategoryMappingRepository(session),
        SqlAlchemyTaxProfileRepository(session),
        SqlAlchemyCategoryRepository(session),
    )


def get_update_mapping_command(
    session: Annotated[Session, Depends(get_db)],
) -> UpdateMexicoTaxCategoryMappingCommand:
    return UpdateMexicoTaxCategoryMappingCommand(
        SqlAlchemyMexicoTaxCategoryMappingRepository(session)
    )


def get_classify_command(
    session: Annotated[Session, Depends(get_db)],
) -> ClassifyMexicoTaxTransactionCommand:
    return ClassifyMexicoTaxTransactionCommand(
        SqlAlchemyMexicoTaxTransactionOverrideRepository(session),
        SqlAlchemyTaxProfileRepository(session),
        SqlAlchemyTransactionRepository(session),
    )


def get_calculate_command(
    session: Annotated[Session, Depends(get_db)],
) -> CalculateMexicoTaxPeriodCommand:
    return CalculateMexicoTaxPeriodCommand(
        periods=SqlAlchemyTaxPeriodRepository(session),
        configurations=SqlAlchemyMexicoTaxConfigurationRepository(session),
        mappings=SqlAlchemyMexicoTaxCategoryMappingRepository(session),
        overrides=SqlAlchemyMexicoTaxTransactionOverrideRepository(session),
        details=SqlAlchemyMexicoTaxDetailsRepository(session),
        evidence=SqlAlchemyTaxEvidenceRepository(session),
        withholdings=SqlAlchemyMexicoTaxWithholdingRepository(session),
        read=SqlAlchemyMexicoTaxReadRepository(session),
        calculations=SqlAlchemyTaxCalculationRepository(session),
        snapshots=SqlAlchemyMexicoTaxSnapshotRepository(session),
    )


def get_configuration_query(
    session: Annotated[Session, Depends(get_db)],
) -> GetMexicoTaxConfigurationQuery:
    return GetMexicoTaxConfigurationQuery(
        SqlAlchemyMexicoTaxConfigurationRepository(session),
        SqlAlchemyTaxProfileRepository(session),
    )


def get_catalogs_query(
    session: Annotated[Session, Depends(get_db)],
) -> ListMexicoTaxCatalogsQuery:
    return ListMexicoTaxCatalogsQuery(SqlAlchemyMexicoTaxCatalogRepository(session))


def get_list_mappings_query(
    session: Annotated[Session, Depends(get_db)],
) -> ListMexicoCategoryMappingsQuery:
    return ListMexicoCategoryMappingsQuery(SqlAlchemyMexicoTaxCategoryMappingRepository(session))


def get_unclassified_query(
    session: Annotated[Session, Depends(get_db)],
) -> ListUnclassifiedTaxTransactionsQuery:
    return ListUnclassifiedTaxTransactionsQuery(SqlAlchemyMexicoTaxReadRepository(session))


def get_workpaper_query(
    session: Annotated[Session, Depends(get_db)],
) -> GetMexicoTaxWorkpaperQuery:
    return GetMexicoTaxWorkpaperQuery(
        SqlAlchemyTaxPeriodRepository(session),
        SqlAlchemyTaxCalculationRepository(session),
        SqlAlchemyMexicoTaxSnapshotRepository(session),
        SqlAlchemyMexicoTaxReadRepository(session),
    )


def get_summary_query(
    session: Annotated[Session, Depends(get_db)],
) -> GetMexicoTaxSummaryQuery:
    return GetMexicoTaxSummaryQuery(
        SqlAlchemyTaxProfileRepository(session),
        SqlAlchemyMexicoTaxConfigurationRepository(session),
        SqlAlchemyTaxPeriodRepository(session),
        SqlAlchemyTaxCalculationRepository(session),
        SqlAlchemyMexicoTaxSnapshotRepository(session),
        SqlAlchemyTaxPaymentRepository(session),
        SqlAlchemyTaxReadRepository(session),
    )
