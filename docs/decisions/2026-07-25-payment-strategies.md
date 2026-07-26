# 2026-07-25 — Payment strategies orient, never execute

**Type:** Product + domain  
**Status:** Accepted  
**Sprint:** [6.4](../roadmap/sprint-6.4-payment-strategies.md)

## Decision

1. Organization stores one `debt_strategy`: `avalanche` | `snowball` | `minimum_only` | `manual`.  
2. Strategies produce **ranked projections + reason codes** only.  
3. Hierarchy: overdue → due soon → at-risk → strategy → manual priority.  
4. Never invent extra payment amounts without an explicit debt budget.  
5. Never assume missing interest rate is 0%.  
6. FE localizes `reason_code`; backend does not persist translated strings as source of truth.

## Why

Users need guidance under stress without WealthOS silently moving their money or lying about affordability.
