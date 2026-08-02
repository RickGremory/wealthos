# Decision: RecurringRule + RecurringRuleVersion from day one

**Date:** 2026-08-01  
**Status:** Accepted  
**Related:** [RFC-005](../rfc/RFC-005-recurring-engine.md) · [Sprint 9.3](../roadmap/sprint-9.3-persistence-lifecycle.md)

---

## Context

9.1 modeled a rich `RecurringRule`. Real products change amount or schedule mid-series (“rent rises from September”). Flattening all config onto one row forces destructive edits or ad-hoc snapshots later.

## Decision

1. Persist a **series shell** (`recurring_rules`) and **temporal versions** (`recurring_rule_versions`).  
2. Money, pattern, accounts, and certainty live **only** on versions.  
3. Effective periods for one rule **never overlap**.  
4. Simple descriptive edits may update the current version; structural edits close the current version and open a new one with `effective_from`.  
5. Occurrence keys remain `recurring:{rule_id}:occurrence:{date}` — **version id is not part of the key**.  
6. Soft-archive rules; soft-deactivate exceptions.  
7. Planning/Calendar talk to a **projection** port, never Recurring ORM.

## Consequences

- Slightly more tables/code upfront; much safer mid-series changes.  
- Generator (9.2) receives one version slice at a time from a version resolver.  
- UX (9.4) must ask “desde cuándo” on structural edits.  
- Mirrors temporal config patterns (price lists / contracts) without becoming an ERP clone.
