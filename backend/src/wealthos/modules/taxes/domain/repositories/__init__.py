"""Repository protocols for taxes."""

from wealthos.modules.taxes.domain.repositories.tax_calculation_repository import (
    TaxCalculationRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_category_mapping_repository import (
    TaxCategoryMappingRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_payment_repository import (
    TaxPaymentRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_period_repository import (
    TaxPeriodRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_profile_repository import (
    TaxProfileRepository,
)
from wealthos.modules.taxes.domain.repositories.tax_read_repository import TaxReadRepository
from wealthos.modules.taxes.domain.repositories.tax_rule_repository import TaxRuleRepository
from wealthos.modules.taxes.domain.repositories.tax_transaction_override_repository import (
    TaxTransactionOverrideRepository,
)

__all__ = [
    "TaxCalculationRepository",
    "TaxCategoryMappingRepository",
    "TaxPaymentRepository",
    "TaxPeriodRepository",
    "TaxProfileRepository",
    "TaxReadRepository",
    "TaxRuleRepository",
    "TaxTransactionOverrideRepository",
]
