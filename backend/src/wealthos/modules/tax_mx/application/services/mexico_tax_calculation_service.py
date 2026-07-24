"""Mexico tax classifier and monthly calculation services."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from wealthos.modules.tax_mx.domain.entities.mexico_tax_classification import (
    MexicoTaxCategoryMapping,
    MexicoTaxTransactionOverride,
)
from wealthos.modules.tax_mx.domain.entities.mexico_tax_configuration import (
    MexicoTaxConfiguration,
)
from wealthos.modules.tax_mx.domain.entities.tax_evidence import MexicoTransactionTaxDetails

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")
_HUNDRED = Decimal("100")
ENGINE = "mexico_configured_rate"
ENGINE_VERSION = "1.0.0"
CATALOG_VERSION = "v1"


@dataclass(frozen=True, slots=True)
class MexicoTaxTransactionView:
    transaction_id: UUID
    transaction_type: str
    status: str
    occurred_on: date
    amount: Decimal
    currency: str
    category_id: UUID | None
    description: str
    updated_at: date | None = None
    linked_tax_payment: bool = False
    amount_includes_vat: bool | None = None


@dataclass(frozen=True, slots=True)
class ClassifiedMexicoTransaction:
    transaction: MexicoTaxTransactionView
    income_treatment: str | None
    expense_treatment: str | None
    vat_treatment: str
    deductibility_percentage: Decimal
    vat_creditable_percentage: Decimal
    requires_cfdi: bool
    source: str  # override | mapping | default | excluded


@dataclass(frozen=True, slots=True)
class TaxWarning:
    code: str
    message: str
    transaction_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class TaxDataQuality:
    total_transactions: int
    classified_transactions: int
    unclassified_transactions: int
    transactions_requiring_evidence: int
    missing_evidence: int
    mismatched_evidence: int
    completeness_percentage: Decimal


@dataclass(frozen=True, slots=True)
class MexicoVATResult:
    output_vat: Decimal
    identified_input_vat: Decimal
    creditable_vat: Decimal
    withheld_vat: Decimal
    due: Decimal
    credit_balance: Decimal


@dataclass(frozen=True, slots=True)
class MexicoIncomeTaxResult:
    taxable_income: Decimal
    deductible_expenses: Decimal
    estimation_base: Decimal
    estimated_before_withholdings: Decimal
    withheld: Decimal
    due: Decimal
    credit: Decimal


@dataclass(frozen=True, slots=True)
class MexicoMonthlyTaxWorkpaper:
    period_id: UUID
    currency: str
    collected_income: Decimal
    taxable_income: Decimal
    exempt_income: Decimal
    paid_expenses: Decimal
    deductible_expenses: Decimal
    non_deductible_expenses: Decimal
    output_vat: Decimal
    identified_input_vat: Decimal
    creditable_vat: Decimal
    withheld_vat: Decimal
    vat_due: Decimal
    vat_credit_balance: Decimal
    estimated_income_tax: Decimal
    withheld_income_tax: Decimal
    income_tax_due: Decimal
    income_tax_credit: Decimal
    estimated_total_due: Decimal
    quality: TaxDataQuality
    warnings: tuple[TaxWarning, ...] = ()
    lines: tuple[dict, ...] = ()
    configuration_version: int = 1
    catalog_version: str = CATALOG_VERSION
    calculation_engine: str = ENGINE
    calculation_engine_version: str = ENGINE_VERSION


@dataclass(frozen=True, slots=True)
class ClassificationBundle:
    mappings: dict[UUID, MexicoTaxCategoryMapping]
    overrides: dict[UUID, MexicoTaxTransactionOverride]
    details: dict[UUID, MexicoTransactionTaxDetails]
    evidence_status_by_tx: dict[UUID, str] = field(default_factory=dict)
    withholdings_income_tax: dict[UUID, Decimal] = field(default_factory=dict)
    withholdings_vat: dict[UUID, Decimal] = field(default_factory=dict)


class MexicoTaxClassifier:
    def classify(
        self,
        tx: MexicoTaxTransactionView,
        bundle: ClassificationBundle,
    ) -> ClassifiedMexicoTransaction | None:
        if tx.status != "posted":
            return None
        if tx.transaction_type in {"transfer", "adjustment"} and (
            tx.transaction_id not in bundle.overrides
        ):
            return None
        if tx.linked_tax_payment:
            return ClassifiedMexicoTransaction(
                transaction=tx,
                income_treatment="ignored",
                expense_treatment="ignored",
                vat_treatment="not_subject",
                deductibility_percentage=_ZERO,
                vat_creditable_percentage=_ZERO,
                requires_cfdi=False,
                source="excluded",
            )

        if tx.transaction_id in bundle.overrides:
            override = bundle.overrides[tx.transaction_id]
            return ClassifiedMexicoTransaction(
                transaction=tx,
                income_treatment=(
                    override.income_treatment.value if override.income_treatment else None
                ),
                expense_treatment=(
                    override.expense_treatment.value if override.expense_treatment else None
                ),
                vat_treatment=override.vat_treatment.value,
                deductibility_percentage=override.deductibility_percentage.value,
                vat_creditable_percentage=override.vat_creditable_percentage.value,
                requires_cfdi=override.requires_cfdi,
                source="override",
            )

        if tx.category_id is not None and tx.category_id in bundle.mappings:
            mapping = bundle.mappings[tx.category_id]
            return ClassifiedMexicoTransaction(
                transaction=tx,
                income_treatment=(
                    mapping.income_treatment.value if mapping.income_treatment else None
                ),
                expense_treatment=(
                    mapping.expense_treatment.value if mapping.expense_treatment else None
                ),
                vat_treatment=mapping.vat_treatment.value,
                deductibility_percentage=mapping.deductibility_percentage.value,
                vat_creditable_percentage=mapping.vat_creditable_percentage.value,
                requires_cfdi=mapping.requires_cfdi,
                source="mapping",
            )

        # Defaults for cash professionals.
        if tx.transaction_type == "income":
            return ClassifiedMexicoTransaction(
                transaction=tx,
                income_treatment="taxable",
                expense_treatment=None,
                vat_treatment="taxable",
                deductibility_percentage=_HUNDRED,
                vat_creditable_percentage=_HUNDRED,
                requires_cfdi=False,
                source="default",
            )
        if tx.transaction_type == "expense":
            return ClassifiedMexicoTransaction(
                transaction=tx,
                income_treatment=None,
                expense_treatment="deductible",
                vat_treatment="taxable",
                deductibility_percentage=_HUNDRED,
                vat_creditable_percentage=_HUNDRED,
                requires_cfdi=False,
                source="default",
            )
        return None


class MexicoVATCalculator:
    def calculate(
        self,
        *,
        classified: list[ClassifiedMexicoTransaction],
        bundle: ClassificationBundle,
        default_vat_rate: Decimal,
        currency: str,
    ) -> MexicoVATResult:
        output = _ZERO
        identified_input = _ZERO
        creditable = _ZERO
        withheld = _ZERO

        for item in classified:
            tx = item.transaction
            if tx.currency != currency or item.source == "excluded":
                continue
            details = bundle.details.get(tx.transaction_id)
            rate_fraction = (default_vat_rate / _HUNDRED).quantize(
                Decimal("0.00000001"), rounding=ROUND_HALF_UP
            )

            if tx.transaction_type == "income" and item.vat_treatment == "taxable":
                if details is not None:
                    vat = details.vat_amount.amount
                elif tx.amount_includes_vat is True:
                    total = abs(tx.amount)
                    subtotal = (total / (Decimal("1") + rate_fraction)).quantize(
                        _CENT, rounding=ROUND_HALF_UP
                    )
                    vat = (total - subtotal).quantize(_CENT, rounding=ROUND_HALF_UP)
                elif tx.amount_includes_vat is False:
                    subtotal = abs(tx.amount)
                    vat = (subtotal * rate_fraction).quantize(_CENT, rounding=ROUND_HALF_UP)
                else:
                    continue
                output += vat
                withheld += bundle.withholdings_vat.get(tx.transaction_id, _ZERO)
                if details is not None:
                    withheld += details.withheld_vat.amount

            if tx.transaction_type == "expense" and item.vat_treatment == "taxable":
                if details is not None:
                    vat = details.vat_amount.amount
                elif tx.amount_includes_vat is True:
                    total = abs(tx.amount)
                    subtotal = (total / (Decimal("1") + rate_fraction)).quantize(
                        _CENT, rounding=ROUND_HALF_UP
                    )
                    vat = (total - subtotal).quantize(_CENT, rounding=ROUND_HALF_UP)
                elif tx.amount_includes_vat is False:
                    subtotal = abs(tx.amount)
                    vat = (subtotal * rate_fraction).quantize(_CENT, rounding=ROUND_HALF_UP)
                else:
                    continue
                identified_input += vat
                portion = (vat * item.vat_creditable_percentage / _HUNDRED).quantize(
                    _CENT, rounding=ROUND_HALF_UP
                )
                creditable += portion

        net = output - creditable - withheld
        due = max(net, _ZERO).quantize(_CENT, rounding=ROUND_HALF_UP)
        credit = abs(min(net, _ZERO)).quantize(_CENT, rounding=ROUND_HALF_UP)
        return MexicoVATResult(
            output_vat=output.quantize(_CENT, rounding=ROUND_HALF_UP),
            identified_input_vat=identified_input.quantize(_CENT, rounding=ROUND_HALF_UP),
            creditable_vat=creditable.quantize(_CENT, rounding=ROUND_HALF_UP),
            withheld_vat=withheld.quantize(_CENT, rounding=ROUND_HALF_UP),
            due=due,
            credit_balance=credit,
        )


@dataclass(frozen=True, slots=True)
class MexicoIncomeTaxContext:
    configuration: MexicoTaxConfiguration
    taxable_income: Decimal
    deductible_expenses: Decimal
    withheld_income_tax: Decimal
    currency: str


class ConfiguredRateIncomeTaxCalculator:
    def calculate(self, context: MexicoIncomeTaxContext) -> MexicoIncomeTaxResult:
        config = context.configuration
        assert config.income_tax_estimation_rate is not None
        assert config.income_tax_estimation_base is not None
        if config.income_tax_estimation_base.value == "net_taxable_income":
            base = max(context.taxable_income - context.deductible_expenses, _ZERO)
        else:
            base = context.taxable_income
        rate = config.income_tax_estimation_rate.as_fraction()
        estimated = (base * rate).quantize(_CENT, rounding=ROUND_HALF_UP)
        net = estimated - context.withheld_income_tax
        due = max(net, _ZERO).quantize(_CENT, rounding=ROUND_HALF_UP)
        credit = abs(min(net, _ZERO)).quantize(_CENT, rounding=ROUND_HALF_UP)
        return MexicoIncomeTaxResult(
            taxable_income=context.taxable_income,
            deductible_expenses=context.deductible_expenses,
            estimation_base=base.quantize(_CENT, rounding=ROUND_HALF_UP),
            estimated_before_withholdings=estimated,
            withheld=context.withheld_income_tax,
            due=due,
            credit=credit,
        )


class MexicoTaxCalculationService:
    def __init__(
        self,
        classifier: MexicoTaxClassifier | None = None,
        vat_calculator: MexicoVATCalculator | None = None,
        income_tax_calculator: ConfiguredRateIncomeTaxCalculator | None = None,
    ) -> None:
        self._classifier = classifier or MexicoTaxClassifier()
        self._vat = vat_calculator or MexicoVATCalculator()
        self._isr = income_tax_calculator or ConfiguredRateIncomeTaxCalculator()

    def calculate(
        self,
        *,
        period_id: UUID,
        configuration: MexicoTaxConfiguration,
        transactions: list[MexicoTaxTransactionView],
        bundle: ClassificationBundle,
        currency: str,
    ) -> MexicoMonthlyTaxWorkpaper:
        warnings: list[TaxWarning] = []
        classified: list[ClassifiedMexicoTransaction] = []
        collected = _ZERO
        taxable_income = _ZERO
        exempt_income = _ZERO
        paid_expenses = _ZERO
        deductible = _ZERO
        non_deductible = _ZERO
        withheld_isr = _ZERO

        relevant = 0
        classified_count = 0
        unclassified = 0
        requiring_evidence = 0
        missing_evidence = 0
        mismatched = 0

        for tx in transactions:
            if tx.currency != currency:
                warnings.append(
                    TaxWarning("currency_mismatch", "Currency mismatch.", tx.transaction_id)
                )
                continue
            if tx.status != "posted":
                continue
            if tx.transaction_type in {"transfer", "adjustment"} and (
                tx.transaction_id not in bundle.overrides
            ):
                continue
            if tx.linked_tax_payment:
                continue

            relevant += 1
            item = self._classifier.classify(tx, bundle)
            if item is None or item.source == "default":
                # Defaults still count as classified for V1 ops, but missing explicit
                # mapping/override is tracked as soft unclassified when required.
                if item is None:
                    unclassified += 1
                    warnings.append(
                        TaxWarning(
                            "missing_classification",
                            "Transaction lacks tax classification.",
                            tx.transaction_id,
                        )
                    )
                    continue
            if item.source in {"mapping", "override", "default"}:
                classified_count += 1
            classified.append(item)

            amount = abs(tx.amount)
            details = bundle.details.get(tx.transaction_id)
            if item.requires_cfdi or configuration.requires_invoice_evidence:
                requiring_evidence += 1
                status = bundle.evidence_status_by_tx.get(tx.transaction_id, "missing")
                if status == "missing":
                    missing_evidence += 1
                    warnings.append(
                        TaxWarning(
                            "missing_evidence",
                            "Required fiscal evidence is missing.",
                            tx.transaction_id,
                        )
                    )
                elif status == "mismatch":
                    mismatched += 1

            if tx.transaction_type == "income":
                collected += amount
                treatment = item.income_treatment or "taxable"
                if treatment == "exempt":
                    exempt_income += details.subtotal.amount if details else amount
                elif treatment in {"taxable", "withheld"}:
                    taxable_income += (
                        details.subtotal.amount
                        if details
                        else (self._derive_subtotal(tx, configuration) or amount)
                    )
                withheld_isr += bundle.withholdings_income_tax.get(tx.transaction_id, _ZERO)
                if details is not None:
                    withheld_isr += details.withheld_income_tax.amount
            elif tx.transaction_type == "expense":
                paid_expenses += amount
                treatment = item.expense_treatment or "deductible"
                base = (
                    details.subtotal.amount
                    if details
                    else (self._derive_subtotal(tx, configuration) or amount)
                )
                if treatment == "deductible":
                    deductible += base
                elif treatment == "partially_deductible":
                    deductible += (base * item.deductibility_percentage / _HUNDRED).quantize(
                        _CENT, rounding=ROUND_HALF_UP
                    )
                    non_deductible += (
                        base - (base * item.deductibility_percentage / _HUNDRED)
                    ).quantize(_CENT, rounding=ROUND_HALF_UP)
                elif treatment == "non_deductible":
                    non_deductible += base

        vat_rate = (
            configuration.default_vat_rate.value
            if configuration.default_vat_rate is not None
            else Decimal("16")
        )
        vat = self._vat.calculate(
            classified=classified,
            bundle=bundle,
            default_vat_rate=vat_rate,
            currency=currency,
        )
        isr = self._isr.calculate(
            MexicoIncomeTaxContext(
                configuration=configuration,
                taxable_income=taxable_income.quantize(_CENT, rounding=ROUND_HALF_UP),
                deductible_expenses=deductible.quantize(_CENT, rounding=ROUND_HALF_UP),
                withheld_income_tax=withheld_isr.quantize(_CENT, rounding=ROUND_HALF_UP),
                currency=currency,
            )
        )
        total_due = (isr.due + vat.due).quantize(_CENT, rounding=ROUND_HALF_UP)
        without_blocking = max(relevant - unclassified - missing_evidence - mismatched, 0)
        completeness = (
            (Decimal(without_blocking) / Decimal(relevant) * _HUNDRED).quantize(_CENT)
            if relevant
            else _HUNDRED
        )
        quality = TaxDataQuality(
            total_transactions=relevant,
            classified_transactions=classified_count,
            unclassified_transactions=unclassified,
            transactions_requiring_evidence=requiring_evidence,
            missing_evidence=missing_evidence,
            mismatched_evidence=mismatched,
            completeness_percentage=completeness,
        )
        lines = (
            {
                "component": "income_tax",
                "description": "ISR estimado configurable",
                "amount": str(isr.estimated_before_withholdings),
            },
            {
                "component": "income_tax_withheld",
                "description": "ISR retenido",
                "amount": str(isr.withheld),
            },
            {
                "component": "vat_output",
                "description": "IVA trasladado",
                "amount": str(vat.output_vat),
            },
            {
                "component": "vat_creditable",
                "description": "IVA acreditable",
                "amount": str(vat.creditable_vat),
            },
        )
        return MexicoMonthlyTaxWorkpaper(
            period_id=period_id,
            currency=currency,
            collected_income=collected.quantize(_CENT, rounding=ROUND_HALF_UP),
            taxable_income=isr.taxable_income,
            exempt_income=exempt_income.quantize(_CENT, rounding=ROUND_HALF_UP),
            paid_expenses=paid_expenses.quantize(_CENT, rounding=ROUND_HALF_UP),
            deductible_expenses=isr.deductible_expenses,
            non_deductible_expenses=non_deductible.quantize(_CENT, rounding=ROUND_HALF_UP),
            output_vat=vat.output_vat,
            identified_input_vat=vat.identified_input_vat,
            creditable_vat=vat.creditable_vat,
            withheld_vat=vat.withheld_vat,
            vat_due=vat.due,
            vat_credit_balance=vat.credit_balance,
            estimated_income_tax=isr.estimated_before_withholdings,
            withheld_income_tax=isr.withheld,
            income_tax_due=isr.due,
            income_tax_credit=isr.credit,
            estimated_total_due=total_due,
            quality=quality,
            warnings=tuple(warnings),
            lines=lines,
            configuration_version=configuration.version,
        )

    def _derive_subtotal(
        self,
        tx: MexicoTaxTransactionView,
        configuration: MexicoTaxConfiguration,
    ) -> Decimal | None:
        if configuration.default_vat_rate is None or tx.amount_includes_vat is None:
            return None
        rate = configuration.default_vat_rate.as_fraction()
        amount = abs(tx.amount)
        if tx.amount_includes_vat:
            return (amount / (Decimal("1") + rate)).quantize(_CENT, rounding=ROUND_HALF_UP)
        return amount
