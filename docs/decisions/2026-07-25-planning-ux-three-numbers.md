# 2026-07-25 — Planning UX: three numbers and simulation isolation

**Type:** Product / UX  
**Status:** Accepted  
**Sprint:** [8.4](../roadmap/sprint-8.4-planning-ux-scenarios.md)

## Decision

1. **Planeación** (`/app/planning`) is the module surface; Safe To Spend is a capability inside it — not the nav name.  
2. Always separate **Saldo actual**, **Disponible para usar**, and **Saldo proyectado**.  
3. “What if?” scenarios are **request-scoped simulations** using the same backend engine; they never mutate real data without an explicit convert action.  
4. Product language for reservations: **fondos protegidos**.  
5. Frontend never reimplements projection math.

## Why

Users otherwise think the product is “wrong” when spendable &lt; balance or ending balance &gt; spendable. Simulation without a hard isolation boundary risks accidental ledger changes.

## Consequences

- Dashboard deep-links into Planning with currency + horizon  
- Reason codes drive narrative; no fake confidence percentages  
- Settings live on `/app/planning/settings`  
