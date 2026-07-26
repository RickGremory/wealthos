# 2026-07-25 — Commitments UX: Next Action pattern

**Type:** Product / UX  
**Status:** Accepted  
**Sprint:** [6.2 UX & User Flows](../roadmap/sprint-6.2-commitments-ux.md)

## Decision

Every Financial Commitment detail (and, over time, Goals / Taxes / Planning / Dashboard widgets) leads with a fixed section:

**What should I do next?**

One clear action sentence derived from schedule, minimums, and status — not a wall of numbers the user must interpret alone.

Paying a commitment opens **New Transfer** with the liability preselected. There is no separate “Make Payment” ledger.

## Why

Debts are stressful; the UI must orient before it informs. The same “orient → act” pattern becomes part of WealthOS product identity.

## Consequences

- Detail layout: Next Action → metrics → transaction history  
- Copy system needed for overdue / due soon / unconfigured / paid off  
- Dashboard commitments widget stays to three signals only (6.2)
