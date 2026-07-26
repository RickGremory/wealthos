# 2026-07-25 — Safe To Spend as Financial Projection

**Type:** Product + domain  
**Status:** Accepted (concept; domain model via [RFC-004](../rfc/RFC-004-planning-projection.md) · Sprint 8.1)  
**Sprint:** [Sprint 8 — Planning & Safe To Spend](../roadmap/sprint-8-planning-safe-to-spend.md)

## Decision

**Safe To Spend is not a formula stored on an account.**  
It is the **consequence** of a **Financial Projection** (`PlanningProjection`) calculated by Planning.

Planning **orchestrates** facts and forecasts from Accounts, Transactions, Commitments, Goals, Taxes, Recurring (when available), and Timeline context. It **never** owns balances, creates transactions, pays obligations, or mutates goals.

## Why

Knowing your balance describes the past and present.  
Knowing what you can safely spend answers *¿Cuánto dinero puedo usar hoy sin comprometer mi futuro?* — the daily reason to open WealthOS.

## Consequences

- Introduce **Principle 10** — Not all available money is spendable money.  
- Classify money as **Disponible / Comprometido / Reservado / Gastado**.  
- Separate **Facts** (confirmed) from **Forecasts** (projected) in every projection result.  
- Persist only **PlanningSettings** (org preferences), never `safe_to_spend` itself.  
- Calculation via independent **policies**, not a single mega-method.  
- Horizons MVP: today / 7d / 30d / 90d only.

## Related

[RFC-004](../rfc/RFC-004-planning-projection.md) · [Sprint 8.1](../roadmap/sprint-8.1-planning-domain-model.md) · [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md)
