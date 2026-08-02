# Sprint 9.6 — Foreign Currency Transfers

**Status:** Done  
**Parent:** Transactions ledger / P09 multi-currency

## Objective

Register a real FX conversion between own accounts (e.g. HSBC MXN → Hapi USD) without pretending both legs share one amount.

## Rules

- Same-currency transfers stay unchanged and keep the cross-currency block.
- FX requires **different** account currencies.
- Capture **source amount** + **destination amount**; derive `effective_exchange_rate = source / destination` (units of source currency per 1 unit of destination).
- Optional fee posts as a separate **adjustment** on the source account (source currency) when provided.
- Parent entity `fx_transfers` links two (or three) posted **adjustment** legs via `related_resource_type = fx_transfer`.
- No market FX API; no consolidated net-worth in a base currency.

## API

`POST /api/v1/organizations/{organization_id}/fx-transfers`

## UX

When transfer accounts have different currencies, keep the block and offer **Registrar conversión**. That mode captures sent amount, received amount, optional fee, and shows the derived effective rate.

## Out of scope

- Unrealized FX gain/loss
- Broker cash vs investment split
- Editing/voiding the FX aggregate as one atomic reverse (void individual legs for now)
