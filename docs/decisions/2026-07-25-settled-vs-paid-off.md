# 2026-07-25 — Settled vs paid off (revolving credit)

**Type:** Domain refinement of [RFC-002](../rfc/RFC-002-financial-commitments.md)  
**Status:** Accepted  
**Sprint:** [6.4](../roadmap/sprint-6.4-payment-strategies.md)

## Decision

**Zero balance ≠ permanent paid off** for open revolving products (credit cards, lines of credit).

| State | Meaning |
|-------|---------|
| Settled / paid currently | Balance is zero now; commitment may still receive charges |
| Closed | Product ended; should not receive new charges |
| Paid off | For installment loans: balance zero **and** (account closed or explicit user confirmation) |

Open cards with zero balance stay eligible to **reopen** on new charges without a false “fully paid forever” celebration unless the user closes the product.

## Why

Cards routinely hit zero and are used again. Auto-`paid_off` on balance alone misleads and breaks strategy eligibility.

## Consequences

- RFC-002 auto-close rule is narrowed for revolving types.  
- UX “Paid Off” celebration for cards requires close/confirm or explicit product end.  
- Strategy eligibility excludes zero-balance settled open cards from Avalanche/Snowball ranks.
