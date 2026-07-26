# 2026-07-25 — Safe To Spend chronological trough

**Type:** Domain algorithm  
**Status:** Accepted  
**Sprint:** [8.2](../roadmap/sprint-8.2-safe-to-spend-algorithm.md)  
**Parent decision:** [Safe To Spend as Financial Projection](./2026-07-25-safe-to-spend-projection.md)

## Decision

Safe To Spend is derived from the **minimum projected liquid balance** across the horizon (including t0), after conservative same-day ordering and certainty filters — **not** from ending balance alone.

```text
safe_to_spend = max(0, min_balance(t) − required_safety_reserve)
```

Uncertain **income** must not inflate spendable cash; probable **outflows** reduce it. Results stay explainable (breakdown + alerts + confidence) and deterministic given `PlanningContext`.

## Why

An ending balance after a future payday can look healthy while the user cannot survive an earlier rent payment. Ending-balance formulas produce dangerous recommendations.

## Consequences

- Engine is a pure function of `PlanningContext`  
- Policies listed in Sprint 8.2 are the calculation spine  
- `safe_to_spend` remains non-persisted  
