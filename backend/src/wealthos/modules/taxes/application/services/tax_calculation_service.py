"""Pure tax calculation service — no repository access."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from wealthos.modules.taxes.domain.entities.tax_calculation import (
    TaxCalculation,
    TaxCalculationLine,
)
from wealthos.modules.taxes.domain.entities.tax_profile import TaxProfile
from wealthos.modules.taxes.domain.entities.tax_rule import TaxRule
from wealthos.modules.taxes.domain.value_objects.tax_treatment import TaxTreatment
from wealthos.shared.domain.value_objects.money import Money

_ZERO = Decimal("0.00")
_CENT = Decimal("0.01")
_HUNDRED = Decimal("100")


@dataclass(frozen=True, slots=True)
class TaxTransactionView:
    transaction_id: UUID
    transaction_type: str
    status: str
    occurred_on: date
    amount: Decimal
    currency: str
    category_id: UUID | None
    linked_tax_payment: bool = False


@dataclass(frozen=True, slots=True)
class TaxPaymentView:
    amount: Decimal
    currency: str
    tax_type: str


@dataclass(frozen=True, slots=True)
class ClassifiedAmount:
    treatment: str
    amount: Decimal
    deductible_amount: Decimal


@dataclass(frozen=True, slots=True)
class ClassificationContext:
    category_mappings: dict[UUID, tuple[str, Decimal]]
    transaction_overrides: dict[UUID, tuple[str, Decimal]]


class TaxTransactionClassifier:
    def classify(
        self,
        tx: TaxTransactionView,
        context: ClassificationContext,
    ) -> ClassifiedAmount | None:
        if tx.status != "posted":
            return None
        if tx.transaction_type in {"transfer", "adjustment"}:
            return None
        amount = abs(Decimal(str(tx.amount))).quantize(_CENT, rounding=ROUND_HALF_UP)
        if tx.linked_tax_payment:
            return ClassifiedAmount("ignored", amount, _ZERO)

        if tx.transaction_id in context.transaction_overrides:
            treatment, pct = context.transaction_overrides[tx.transaction_id]
        elif tx.category_id is not None and tx.category_id in context.category_mappings:
            treatment, pct = context.category_mappings[tx.category_id]
        elif tx.transaction_type == "income":
            treatment, pct = "taxable_income", _HUNDRED
        elif tx.transaction_type == "expense":
            treatment, pct = "deductible_expense", _HUNDRED
        else:
            return ClassifiedAmount("ignored", amount, _ZERO)

        TaxTreatment(treatment)
        deductible = _ZERO
        if treatment in {"deductible_expense", "partially_deductible_expense"}:
            deductible = (amount * pct / _HUNDRED).quantize(_CENT, rounding=ROUND_HALF_UP)
        return ClassifiedAmount(treatment, amount, deductible)


class TaxCalculationService:
    def __init__(self, classifier: TaxTransactionClassifier | None = None) -> None:
        self._classifier = classifier or TaxTransactionClassifier()

    def calculate(
        self,
        *,
        profile: TaxProfile,
        period_id: UUID,
        period_from: date,
        period_to: date,
        rules: list[TaxRule],
        transactions: list[TaxTransactionView],
        payments: list[TaxPaymentView],
        context: ClassificationContext,
        version: int,
        performed_by_user_id: UUID,
    ) -> tuple[TaxCalculation, Decimal]:
        currency = profile.currency.value
        gross = _ZERO
        taxable_income = _ZERO
        deductible = _ZERO

        for tx in transactions:
            if tx.currency != currency:
                continue
            classified = self._classifier.classify(tx, context)
            if classified is None or classified.treatment == "ignored":
                continue
            if tx.transaction_type == "income":
                gross += classified.amount
                if classified.treatment == "taxable_income":
                    taxable_income += classified.amount
            elif tx.transaction_type == "expense":
                deductible += classified.deductible_amount

        taxable_base = max(taxable_income - deductible, _ZERO).quantize(
            _CENT, rounding=ROUND_HALF_UP
        )
        calc_id = uuid4()
        lines: list[TaxCalculationLine] = []
        estimated = _ZERO

        for rule in sorted(rules, key=lambda item: item.priority):
            if not self._rule_applies_to_period(rule, period_from, period_to):
                continue
            base = self._base_for_rule(
                rule,
                gross_income=gross,
                taxable_income=taxable_income,
                deductible_expenses=deductible,
                taxable_base=taxable_base,
                transactions=transactions,
                context=context,
                currency=currency,
            )
            amount, rate = self._apply_rule(rule, base)
            estimated += amount
            lines.append(
                TaxCalculationLine(
                    id=uuid4(),
                    tax_calculation_id=calc_id,
                    tax_rule_id=rule.id,
                    description=rule.name.value,
                    taxable_base=Money(base, currency),
                    rate=rate,
                    calculated_amount=Money(amount, currency),
                )
            )

        estimated = estimated.quantize(_CENT, rounding=ROUND_HALF_UP)
        paid = sum(
            (Decimal(str(item.amount)) for item in payments if item.currency == currency),
            _ZERO,
        ).quantize(_CENT, rounding=ROUND_HALF_UP)

        calculation = TaxCalculation.create(
            organization_id=profile.organization_id,
            tax_period_id=period_id,
            version=version,
            gross_income=Money(gross, currency),
            taxable_income=Money(taxable_income, currency),
            deductible_expenses=Money(deductible, currency),
            taxable_base=Money(taxable_base, currency),
            estimated_tax=Money(estimated, currency),
            calculated_by_user_id=performed_by_user_id,
            lines=lines,
            calculation_id=calc_id,
        )
        return calculation, paid

    def _rule_applies_to_period(self, rule: TaxRule, period_from: date, period_to: date) -> bool:
        if rule.archived_at is not None or not rule.is_active:
            return False
        if rule.effective_from > period_to:
            return False
        if rule.effective_to is not None and rule.effective_to < period_from:
            return False
        return True

    def _base_for_rule(
        self,
        rule: TaxRule,
        *,
        gross_income: Decimal,
        taxable_income: Decimal,
        deductible_expenses: Decimal,
        taxable_base: Decimal,
        transactions: list[TaxTransactionView],
        context: ClassificationContext,
        currency: str,
    ) -> Decimal:
        applies = rule.applies_to.value
        if applies == "gross_income":
            return gross_income
        if applies == "net_income":
            return taxable_base
        if applies == "expenses":
            return deductible_expenses

        total = _ZERO
        categories = set(rule.category_ids)
        for tx in transactions:
            if tx.currency != currency:
                continue
            classified = self._classifier.classify(tx, context)
            if classified is None or classified.treatment == "ignored":
                continue
            if applies == "category_income":
                if tx.transaction_type != "income":
                    continue
                if categories and tx.category_id not in categories:
                    continue
                if classified.treatment != "taxable_income":
                    continue
                total += classified.amount
            elif applies == "category_expense":
                if tx.transaction_type != "expense":
                    continue
                if categories and tx.category_id not in categories:
                    continue
                total += classified.deductible_amount or classified.amount
            elif applies == "transaction_amount":
                if categories and (tx.category_id is None or tx.category_id not in categories):
                    continue
                total += classified.amount
        return total.quantize(_CENT, rounding=ROUND_HALF_UP)

    def _apply_rule(self, rule: TaxRule, base: Decimal) -> tuple[Decimal, Decimal | None]:
        if rule.calculation_method.value == "fixed":
            assert rule.fixed_amount is not None
            return rule.fixed_amount.amount, None
        assert rule.rate is not None
        rate = rule.rate.value
        fraction = rule.rate.as_fraction()
        if rule.tax_inclusion_mode.value == "inclusive" and base > 0:
            denom = Decimal("1") + fraction
            net = (base / denom).quantize(_CENT, rounding=ROUND_HALF_UP)
            return (base - net).quantize(_CENT, rounding=ROUND_HALF_UP), rate
        return (base * fraction).quantize(_CENT, rounding=ROUND_HALF_UP), rate
