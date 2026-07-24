"""Mexico tax mappers."""

from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_category_mapping_mapper import (
    MexicoTaxCategoryMappingMapper,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_configuration_mapper import (
    MexicoTaxConfigurationMapper,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_transaction_override_mapper import (
    MexicoTaxTransactionOverrideMapper,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_tax_withholding_mapper import (
    MexicoTaxWithholdingMapper,
)
from wealthos.modules.tax_mx.infrastructure.mappers.mexico_transaction_tax_details_mapper import (
    MexicoTransactionTaxDetailsMapper,
)
from wealthos.modules.tax_mx.infrastructure.mappers.tax_evidence_mapper import TaxEvidenceMapper

__all__ = [
    "MexicoTaxCategoryMappingMapper",
    "MexicoTaxConfigurationMapper",
    "MexicoTaxTransactionOverrideMapper",
    "MexicoTaxWithholdingMapper",
    "MexicoTransactionTaxDetailsMapper",
    "TaxEvidenceMapper",
]
