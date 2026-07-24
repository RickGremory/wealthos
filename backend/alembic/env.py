from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from wealthos.core.database import Base
from wealthos.core.settings import get_settings
from wealthos.modules.accounts.infrastructure.models import AccountModel  # noqa: F401
from wealthos.modules.categories.infrastructure.models import CategoryModel  # noqa: F401
from wealthos.modules.debts.infrastructure.models import (  # noqa: F401
    DebtModel,
    DebtPaymentModel,
)
from wealthos.modules.goals.infrastructure.models import (  # noqa: F401
    GoalAccountModel,
    GoalManualProgressModel,
    GoalModel,
)

# Import module models so they register on Base.metadata for autogenerate.
from wealthos.modules.identity.infrastructure.models import UserModel  # noqa: F401
from wealthos.modules.organizations.infrastructure.models import (  # noqa: F401
    OrganizationMembershipModel,
    OrganizationModel,
)
from wealthos.modules.planning.infrastructure.models import (  # noqa: F401
    BudgetAllocationMatchModel,
    BudgetAllocationModel,
    BudgetModel,
    CashPlanAccountModel,
    CashPlanItemMatchModel,
    CashPlanItemModel,
    CashPlanModel,
)
from wealthos.modules.tax_mx.infrastructure.models import (  # noqa: F401
    MexicoTaxCalculationSnapshotModel,
    MexicoTaxCategoryMappingModel,
    MexicoTaxConfigurationModel,
    MexicoTaxTransactionOverrideModel,
    MexicoTaxWithholdingModel,
    MexicoTransactionTaxDetailsModel,
    MxTaxCatalogEntryModel,
    MxTaxPaymentDetailModel,
    TaxEvidenceModel,
)
from wealthos.modules.taxes.infrastructure.models import (  # noqa: F401
    TaxCalculationLineModel,
    TaxCalculationModel,
    TaxCategoryMappingModel,
    TaxPaymentModel,
    TaxPeriodModel,
    TaxProfileModel,
    TaxRuleCategoryModel,
    TaxRuleModel,
    TaxTransactionOverrideModel,
)
from wealthos.modules.transactions.infrastructure.models import (  # noqa: F401
    TransactionEntryModel,
    TransactionModel,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
