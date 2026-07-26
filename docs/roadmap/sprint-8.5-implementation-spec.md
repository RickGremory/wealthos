# Sprint 8.5 — Technical SPEC & Implementation Plan

**Status:** Accepted (design closed — execution via [SPEC-004](../../specs/backend/planning/SPEC-004-planning-safe-to-spend.md))  
**Parent:** [Sprint 8](./sprint-8-planning-safe-to-spend.md)  
**Contracts:** [8.1](./sprint-8.1-planning-domain-model.md) · [8.2](./sprint-8.2-safe-to-spend-algorithm.md) · [8.3](./sprint-8.3-planning-integration.md) · [8.4](./sprint-8.4-planning-ux-scenarios.md)

> Day-to-day coding follows **SPEC-004**. Do not reopen 8.1–8.4 for implementation details.

---

## Objective

Turn 8.1–8.4 into an executable plan so Planning ships as a working module:

- persistent settings + manual planned cash flows  
- context builders + adapters  
- chronological projection engine + Safe To Spend  
- scenario simulation  
- `/app/planning` + settings  
- Dashboard summary card  

## Out of scope (still)

Scenario persistence · AI forecasts · FX · bank sync · projection snapshots · push notifications · Timeline material-change events · refinance scenarios · probabilistic models

## Core contract

```text
calculate_projection(context)  →  PlanningProjectionResult
         └── safe_to_spend is one field among many
```

Not a lone `calculate_safe_to_spend()`.

## PR plan (summary)

| PR | Focus |
|----|--------|
| 1 | Foundation: enums, settings, planned CF, migration |
| 2 | Projection engine + policies + unit tests |
| 3 | Adapters, dedupe, settlements, context builder |
| 4 | Planning API |
| 5 | Planning UI (hero → movements → breakdown) |
| 6 | Scenarios API + UI |
| 7 | Dashboard + polish |

## Next after Sprint 8

[Sprint 9 — Recurring Engine](./sprint-9-recurring-engine.md) (when opened) — domain: template vs occurrence vs transaction.
