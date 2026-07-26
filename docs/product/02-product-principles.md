# Product Principles

These principles guide every **product** decision in WealthOS.

They answer *why* we build a feature a certain way.  
ADRs answer *how* we implement it technically.

**Related:** [Manifesto](./00-manifesto.md) · [Vision](./01-product-vision.md) · [PRODUCT_LANGUAGE.md](./PRODUCT_LANGUAGE.md)

When a decision is hard, ask: *Does this align with WealthOS?* If not, it probably should not ship.

---

## Principle 01 — Financial Truth over Convenience

Never show a balance that cannot be explained.

Convenience that invents numbers destroys trust.

---

## Principle 02 — One Source of Truth

Each financial fact has a single origin.

Accounts hold balances. Transactions move money. Debts do not store a second balance. Goals do not own money.

---

## Principle 03 — Money Always Moves

Money does not appear or disappear.

Every change in wealth is a **Transaction** (or an explicit opening adjustment that is itself ledgered).

---

## Principle 04 — Everything Has Context

A number without context does not help.

Amounts relate to an account, a goal, a commitment, a period, or a currency — explicitly.

---

## Principle 05 — Planning Before Automation

First help the user understand.

Then automate.

Automation that skips understanding creates fragile habits. (This supersedes an earlier draft that pushed “automation whenever possible.”)

---

## Principle 06 — Privacy by Design

Financial information belongs to the user.

Do not use data for purposes they would not reasonably expect. Consent stays versioned and reviewable.

---

## Principle 07 — Financial Progress Beats Financial Perfection

The goal is not a perfect user.

The goal is better decisions every month. Reward improvement; do not punish honest mistakes (archive/recover beats silent delete).

---

## Principle 08 — Financial Commitments

Future money already has obligations.

WealthOS makes those commitments visible.

- An **Account** answers: *¿Dónde está mi dinero?*  
- A **Financial Commitment** answers: *¿Qué compromete mi dinero futuro?*

Backend may implement the first commitment type as `Debt` (`modules/debts/`).  
Product UI presents **Obligaciones** — room for taxes and other commitment types later.

See [RFC-002](../rfc/RFC-002-financial-commitments.md).

---

## Supporting heuristics (still true)

These remain useful and align with the principles above:

- **Clarity over complexity** — if finances are not clear in minutes, we failed (P01, P04).  
- **Goals before reports** — destinations beat vanity dashboards (P04, P07).  
- **Education through the product** — teach healthy habits in context (P05, P07).

---

## Status

Accepted 2026-07-25. Living document — evolve carefully; record supersessions in the [decision log](../decisions/05-decision-log.md).
