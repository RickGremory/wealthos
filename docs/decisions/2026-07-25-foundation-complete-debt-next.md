# 2026-07-25 — Foundation complete; Debt next (skip polish sprint)

**Type:** Product + process  
**Status:** Accepted  
**Milestone tag:** `v0.5.0-foundation`

## Decision

1. **Close the MVP foundation** as a named git milestone (`v0.5.0-foundation`).  
   Scope closed: modular architecture, navigable core loop (accounts → transactions → dashboard → goals), legal consent, responsive UI, demo seed, updated README.

2. **Do not run another dedicated polish sprint** before the next domain module. Remaining polish is opportunistic (bugs found while building).

3. **Start Sprint 6 — Debt Management** as the next product module — because it maximizes user value once income/expenses are under control, not merely because it was next on a list.

4. From this point, treat WealthOS as a product that **may have real users**: design for recovery from mistakes, multi-account scale, migrations, and feedback — not only for feature completeness.

## Why Debt now

Today WealthOS answers:

- How much do I have?
- What did I spend on?
- How am I doing on goals?

It does **not** yet answer: **How much do I actually owe?**

For independents, wealth is:

```text
Assets − Liabilities = Net Worth
```

Without liabilities, net worth is inflated. Debts also unlock better Dashboard (assets / liabilities / net worth), Goal trade-offs, Planning cash-flow accuracy, and later AI payoff advice (avalanche / snowball / refinance).

## Product mindset (from here)

When designing Debt (and everything after), prefer questions like:

- What if a user has 200 accounts or many debts?
- What if they delete a debt by mistake?
- How do we migrate schema between versions?
- What usage metrics and early-user feedback do we need?

## Explicitly deferred

- Dedicated Sprint 5.R polish pass as a blocking phase
- Taxes / Budgets / AI ahead of Debts
- Publishing a hosted “release” — the tag is a **reference point**, not a go-to-market version

## Related

- [Module roadmap](../roadmap/module-roadmap.md)
- [Sprint 6 — Debt Management](../roadmap/sprint-6-debt-management.md)
- [EPIC-005](../epics/EPIC-005-debts.md)
- [Releases](../../planning/RELEASES.md)
