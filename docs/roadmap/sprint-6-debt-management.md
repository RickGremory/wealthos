# Sprint 6 — Debt Management

**Status:** Ready to start  
**Epic:** [EPIC-005](../epics/EPIC-005-debts.md)  
**Decision:** [2026-07-25 foundation complete; Debt next](../decisions/2026-07-25-foundation-complete-debt-next.md)  
**Baseline tag:** `v0.5.0-foundation`

---

## Why this sprint

After Goals, the highest-value unanswered question for independents is:

> How much do I really owe?

Debts make net worth honest and unlock richer Dashboard, Goals trade-offs, Planning cash flow, and later AI strategies.

---

## Product questions this sprint must answer

| Question | Answer shape |
|----------|----------------|
| What do I owe? | List of debts with balances, rates, minimums |
| What is my real net worth? | Assets − Liabilities (by currency, no silent FX) |
| What am I paying toward debt? | Payments as transactions (or explicit debt payments linked to the ledger) |
| Can I undo a mistake? | Archive / soft-delete; no silent hard wipe of history |

---

## Exit criteria (Sprint 6 complete)

- [ ] Domain model for debts under `modules/debts/` (org-scoped, UUID, UTC)
- [ ] CRUD (+ archive) API for debts
- [ ] Payments reduce principal via the **transaction** source of truth (or an explicit, auditable link to it)
- [ ] Dashboard can expose Assets / Liabilities / Net Worth (even if v1 is simple)
- [ ] Nuxt UI: list, create/edit, detail, archive — same quality bar as Goals
- [ ] Demo seed optionally includes at least one sample debt
- [ ] Tests for org isolation, archive recovery path, and balance math invariants
- [ ] SPEC(s) closed or marked Completed for shipped slices

---

## Suggested slices

### 6.1 — Domain & persistence

- Debt aggregate: name, type (credit_card, loan, mortgage, other), principal/balance, currency, interest rate (APR optional), minimum payment, due day, status (active/archived), notes
- Migration + repository
- Invariants: org scoping; currency explicit; never invent FX; soft archive preferred over hard delete

### 6.2 — API

- `GET/POST /organizations/{id}/debts`
- `GET/PATCH` debt by id
- `POST .../archive` (and restore if we support it)
- Payment recording path that does not fork a second ledger

### 6.3 — Dashboard integration

- Liabilities total(s) by currency
- Net worth = assets − liabilities (document gaps if multi-currency)
- Widget / section: outstanding debt summary

### 6.4 — Frontend

- Navigation entry + list / new / detail / edit
- Clear empty states and destructive-action confirmation (archive)
- Mobile parity with existing finance screens

### 6.5 — Seed, docs, polish-in-place

- Extend `seed_demo.py` with a sample liability
- README / module README / OpenAPI types regen
- Fix only bugs discovered while shipping Debt (no separate polish sprint)

---

## Design constraints (product mindset)

1. **Mistake recovery** — archive with confirmation; restore or clear audit trail stated in SPEC.
2. **Scale** — list endpoints paginated; no N+1 balance fetches that break at dozens of debts.
3. **Migrations** — every schema change is an Alembic revision; no “fix the DB” for real users later.
4. **Explainability** — every liability total on the Dashboard must be traceable to debt records (and payments to transactions).
5. **Strategies later** — Avalanche / Snowball / refinance advice are **consumers** of Debt data (AI / Planning). Do not hard-code strategy engines into the debt aggregate in 6.x unless a SPEC explicitly needs a minimal payoff ordering helper.

---

## Unlocks after this sprint

| Area | What becomes possible |
|------|------------------------|
| Dashboard | Assets / Liabilities / Net Worth |
| Goals | “Pay card vs save for house” trade-off inputs |
| Planning | Cash flow that includes minimum payments |
| AI | Avalanche / Snowball / refinance recommendations on real data |

---

## Out of scope

- Dedicated polish-only sprint before/after (do in-place)
- Taxes, budgets UI, recurring automation, AI coaching
- Bank sync / Open Banking

---

## How we execute

Same delivery bar as Goals: SPEC (or thin SPEC per slice) → implement → tests → FE → demo seed → commit. Prefer small reviewable slices over a big-bang Debt dump.
