# Sprint 9.6 — Foreign Currency Transfers

**Status:** Done  
**SPEC:** [SPEC-006](../../specs/backend/transactions/SPEC-006-fx-transfers.md)

## Goal

Register real FX conversions between own accounts without treating them as same-currency transfers.

## Outcome

- Same-currency transfer validation kept.
- Cross-currency offers **Registrar conversión**.
- Parent `fx_transfers` + adjustment legs linked by `related_resource_type=fx_transfer`.
- Effective rate = source_amount / destination_amount (no market API).
- Optional fee as separate source-currency adjustment.
