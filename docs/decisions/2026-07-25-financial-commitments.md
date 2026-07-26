# 2026-07-25 — Financial Commitments (Obligaciones)

**Type:** Product  
**Status:** Accepted  
**RFC:** [RFC-002](../rfc/RFC-002-financial-commitments.md)

## Decision

1. Sprint 6 is named **Financial Commitments**, not only “Debt Management.”  
2. Backend module remains `modules/debts/`; first commitment type is **Debt**.  
3. UI presents **Obligaciones** — users think in commitments, not aggregates.  
4. Adopt **Product Principle 08** and the [product language](../product/PRODUCT_LANGUAGE.md) glossary.  
5. Debt balance is never stored on Debt; payments are always Transactions.

## Why

Independents ask what claims their future cash — cards, loans, MSI, later taxes — as one mental model. Naming the sprint and UI for commitments preserves that model without a premature `FinancialCommitment` table.

## Consequences

- Dashboard may evolve from “Pasivos” alone toward “Compromisos financieros.”  
- AI later prioritizes *obligaciones*, not only *deudas*.  
- Existing debts code must converge to [RFC-002](../rfc/RFC-002-financial-commitments.md) invariants (optional rates, creditor, statuses, etc.).
