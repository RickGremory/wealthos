# 2026-07-25 — Financial Timeline

**Type:** Product  
**Status:** Accepted (concept reserved — not implemented)  
**Sprint:** [6.3 Integration](../roadmap/sprint-6.3-commitments-integration.md)

## Decision

Introduce **Financial Timeline** as a WealthOS signature concept: a unified chronological view of the user’s financial life.

It is **not**:

- A new ledger  
- A social activity feed  
- A replacement for module-specific detail screens  

It **is** a composition surface over coherent events from Transactions, Goals, Financial Commitments, Calendar, Taxes, and Planning.

## Why

Per-module histories fragment the story. A single timeline turns WealthOS into a narrative of financial progress — highly differentiated vs expense trackers.

## Consequences (now)

- When modules emit dates/events, prefer shapes that can map to timeline entries later.  
- Observability / domain events (`commitment_paid_off`, etc.) are candidates for timeline ingredients.  
- Do **not** build the Timeline UI in Sprint 6. Document the noun in [PRODUCT_LANGUAGE](../product/PRODUCT_LANGUAGE.md).

## Later

A dedicated Timeline slice (post–Commitments / Taxes / Planning) assembles the spine without redesigning domains.
