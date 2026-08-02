"""FastAPI dependencies for Recurring."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from wealthos.core.database import get_db
from wealthos.modules.organizations.infrastructure.models.organization_model import (
    OrganizationModel,
)
from wealthos.modules.recurring.application.commands.create_exception import (
    CreateRecurringOccurrenceExceptionHandler,
    DeactivateRecurringOccurrenceExceptionHandler,
)
from wealthos.modules.recurring.application.commands.create_rule import (
    CreateRecurringRuleHandler,
)
from wealthos.modules.recurring.application.commands.create_rule_version import (
    CreateRecurringRuleVersionHandler,
)
from wealthos.modules.recurring.application.commands.end_archive_rule import (
    ArchiveRecurringRuleHandler,
    EndRecurringRuleHandler,
)
from wealthos.modules.recurring.application.commands.pause_resume_rule import (
    PauseRecurringRuleHandler,
    ResumeRecurringRuleHandler,
)
from wealthos.modules.recurring.application.commands.update_metadata import (
    UpdateRecurringRuleMetadataHandler,
)
from wealthos.modules.recurring.application.queries.list_get_rules import (
    GetRecurringRuleQuery,
    ListRecurringRulesQuery,
)
from wealthos.modules.recurring.application.queries.preview_occurrences import (
    ListRecurringOccurrencesQuery,
    PreviewRecurringRuleQuery,
    PreviewUnsavedRecurringRuleQuery,
)
from wealthos.modules.recurring.infrastructure.persistence.repositories.sqlalchemy_recurring_aggregate_repository import (
    SqlAlchemyRecurringAggregateRepository,
)
from wealthos.modules.recurring.infrastructure.persistence.repositories.sqlalchemy_recurring_settlement_repository import (
    SqlAlchemyRecurringSettlementRepository,
)
from wealthos.shared.persistence import SqlAlchemyUnitOfWork


def get_unit_of_work(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_recurring_repo(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyRecurringAggregateRepository:
    return SqlAlchemyRecurringAggregateRepository(session)


def get_settlement_repo(
    session: Annotated[Session, Depends(get_db)],
) -> SqlAlchemyRecurringSettlementRepository:
    return SqlAlchemyRecurringSettlementRepository(session)


def get_org_timezone(
    organization_id: UUID,
    session: Annotated[Session, Depends(get_db)],
) -> str:
    org = session.get(OrganizationModel, organization_id)
    return org.timezone if org is not None else "America/Cancun"


def get_list_rules_query(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> ListRecurringRulesQuery:
    return ListRecurringRulesQuery(repo)


def get_get_rule_query(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> GetRecurringRuleQuery:
    return GetRecurringRuleQuery(repo)


def get_preview_unsaved_query() -> PreviewUnsavedRecurringRuleQuery:
    return PreviewUnsavedRecurringRuleQuery()


def get_preview_rule_query(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
    settlements: Annotated[
        SqlAlchemyRecurringSettlementRepository,
        Depends(get_settlement_repo),
    ],
) -> PreviewRecurringRuleQuery:
    return PreviewRecurringRuleQuery(repo, settlements)


def get_list_occurrences_query(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
    settlements: Annotated[
        SqlAlchemyRecurringSettlementRepository,
        Depends(get_settlement_repo),
    ],
) -> ListRecurringOccurrencesQuery:
    return ListRecurringOccurrencesQuery(repo, settlements)


def get_create_rule_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> CreateRecurringRuleHandler:
    return CreateRecurringRuleHandler(repo)


def get_update_metadata_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> UpdateRecurringRuleMetadataHandler:
    return UpdateRecurringRuleMetadataHandler(repo)


def get_create_version_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> CreateRecurringRuleVersionHandler:
    return CreateRecurringRuleVersionHandler(repo)


def get_pause_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> PauseRecurringRuleHandler:
    return PauseRecurringRuleHandler(repo)


def get_resume_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> ResumeRecurringRuleHandler:
    return ResumeRecurringRuleHandler(repo)


def get_end_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> EndRecurringRuleHandler:
    return EndRecurringRuleHandler(repo)


def get_archive_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> ArchiveRecurringRuleHandler:
    return ArchiveRecurringRuleHandler(repo)


def get_create_exception_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
    settlements: Annotated[
        SqlAlchemyRecurringSettlementRepository,
        Depends(get_settlement_repo),
    ],
) -> CreateRecurringOccurrenceExceptionHandler:
    return CreateRecurringOccurrenceExceptionHandler(repo, settlements)


def get_deactivate_exception_handler(
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
) -> DeactivateRecurringOccurrenceExceptionHandler:
    return DeactivateRecurringOccurrenceExceptionHandler(repo)


def get_link_settlement_handler(
    session: Annotated[Session, Depends(get_db)],
    repo: Annotated[SqlAlchemyRecurringAggregateRepository, Depends(get_recurring_repo)],
    settlements: Annotated[
        SqlAlchemyRecurringSettlementRepository,
        Depends(get_settlement_repo),
    ],
) -> LinkRecurringOccurrenceTransactionHandler:
    from wealthos.modules.recurring.application.commands.link_transaction import (
        LinkRecurringOccurrenceTransactionHandler,
    )
    from wealthos.modules.recurring.infrastructure.adapters.sqlalchemy_transaction_validation import (
        SqlAlchemyRecurringTransactionValidation,
    )

    return LinkRecurringOccurrenceTransactionHandler(
        repo,
        settlements,
        SqlAlchemyRecurringTransactionValidation(session),
    )


def get_unlink_settlement_handler(
    settlements: Annotated[
        SqlAlchemyRecurringSettlementRepository,
        Depends(get_settlement_repo),
    ],
) -> UnlinkRecurringOccurrenceTransactionHandler:
    from wealthos.modules.recurring.application.commands.link_transaction import (
        UnlinkRecurringOccurrenceTransactionHandler,
    )

    return UnlinkRecurringOccurrenceTransactionHandler(settlements)
