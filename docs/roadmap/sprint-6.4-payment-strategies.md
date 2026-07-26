# Sprint 6.4 — Payment Strategies & Recommendations

**Status:** Accepted  
**Parent:** [Sprint 6 — Financial Commitments](./sprint-6-financial-commitments.md)  
**Depends on:** [RFC-002](../rfc/RFC-002-financial-commitments.md) · [6.2 UX](./sprint-6.2-commitments-ux.md) · [6.3 Integration](./sprint-6.3-commitments-integration.md)  
**Decisions:** [Payment strategies](../decisions/2026-07-25-payment-strategies.md) · [Settled vs paid off](../decisions/2026-07-25-settled-vs-paid-off.md)

> Orient, never auto-pay. Strategies rank and explain; they never create transactions or mutate balances.

---

## Product question

> ¿Qué obligación debería priorizar y por qué?

---

## 1. Initial strategies

| Strategy | Orders by | Goal |
|----------|-----------|------|
| **Avalanche** | Highest interest rate → lowest | Minimize total interest |
| **Snowball** | Lowest balance → highest | Close debts fast (motivation) |
| **Minimum only** | Keep minima current; no extra-payment push | Stay current |
| **Manual** | User emotional priority (`high` / `medium` / `low`) | Full control |

### Tie-breakers

**Avalanche:** overdue → nearest due date → smaller balance  

**Snowball:** overdue → higher rate → nearest due date  

---

## 2. Where the strategy lives

- **Organization-level:** `organization.debt_strategy` ∈ `{avalanche, snowball, minimum_only, manual}`  
- **Not** stored per debt as the primary strategy  
- Each debt keeps **emotional priority** (`high` | `medium` | `low`) for Manual and as a lower-tier signal  

---

## 3. Recommendation shape (projection only)

```json
{
  "strategy": "avalanche",
  "recommended_commitment_id": "uuid",
  "reason_code": "highest_interest_rate",
  "reason": "Tiene la tasa de interés más alta.",
  "minimum_payment": "1250.00",
  "suggested_extra_payment": null
}
```

- `reason` may be FE-localized from `reason_code`; prefer codes from the API.  
- **Do not** invent `suggested_extra_payment` unless an explicit debt budget exists. Unknown liquidity ≠ €300 extra.

---

## 4. Priority hierarchy (before strategy sort)

1. Overdue obligations  
2. Minimum / scheduled payments due soon  
3. At-risk obligations (`defaulted` and similar attention cases)  
4. Selected strategy ordering  
5. Manual emotional priority  

An overdue card always ranks above a higher-rate debt that is not yet due.

---

## 5. Eligibility

**Participates** in Avalanche / Snowball / Minimum ranking when:

- `status = active`  
- derived balance &gt; 0  
- not archived  

**Excluded:** `paid_off`, `paused`, `archived`, and **settled-but-open** cards with zero balance (see §10).

**`defaulted`:** appears as special Needs Attention — not a normal Avalanche/Snowball participant.

---

## 6. Incomplete data — be honest

Never assume missing APR = 0%.

Projection `status`:

| Status | Meaning |
|--------|---------|
| `available` | Enough data for a full ranking under the strategy |
| `partial` | Ranking uses only debts with required fields (e.g. rate for Avalanche) |
| `insufficient_data` | Cannot produce a useful ranking |
| `not_configured` | No strategy set / no eligible debts |
| `unavailable` | Temporarily cannot compute |

Example `partial`:

```json
{
  "status": "partial",
  "strategy": "avalanche",
  "excluded_commitments": 2,
  "message": "La recomendación utiliza únicamente las obligaciones con tasa registrada."
}
```

---

## 7. Commitment next action (derived)

```ts
type CommitmentNextAction =
  | "pay_overdue"
  | "pay_minimum"
  | "pay_priority_debt"
  | "configure_payment"
  | "configure_interest_rate"
  | "review_paused"
  | "no_action_required";
```

FE turns codes into copy (see [6.2 Next Action](./sprint-6.2-commitments-ux.md)).

---

## 8. Minimum vs scheduled payment

| Field | Typical use |
|-------|-------------|
| `minimum_payment` | Credit cards — variable floor |
| `scheduled_payment` | Mortgage / installment — contractual installment |

ViewModel may expose:

- `required_payment`  
- `required_payment_type` ∈ `{minimum, scheduled}`  

Domain **keeps both concepts** distinct.

---

## 9. MSI / installment plans (`installment_plan`)

- Rate often 0% → **last among interest-bearing** in Avalanche (never win on rate alone).  
- Still must meet scheduled installment.  
- Overdue → immediate Needs Attention.  

Useful metadata (V1 optional): `installment_count`, `installments_paid`, `installment_amount`, `next_installment_date`.

No complex multi-purchase MSI under one card in V1 — independent commitment or defer sub-domain.

---

## 10. Cards: settled ≠ closed ≠ permanent paid_off

| Concept | Meaning |
|---------|---------|
| **Settled** / `paid_currently` | Balance is zero **now**; product may still receive charges |
| **Closed** | Financial product ended; should not receive new charges |
| **Paid off** (loans) | Balance zero **and** account closed or user confirmation |

Revolving credit: zero balance must **not** force permanent `paid_off` without close/confirm. Revive when balance returns remains valid for open cards.

Refines [RFC-002](../rfc/RFC-002-financial-commitments.md) auto-close — see [decision](../decisions/2026-07-25-settled-vs-paid-off.md).

---

## 11. Loans (mortgage, personal, auto, …)

```text
balance = 0
+ (account closed OR user confirmation)
= paid_off
```

Avoid auto-closing on a temporary zero from an adjustment error.

---

## 12. Educational comparison only

Compare Avalanche vs Snowball **qualitatively** (“saves interest” vs “closes debts faster”).

Do **not** promise exact savings (€4,238) without reliable schedules, capitalization, fees, and future payments.

Full amortization simulator: out of Sprint 6.

---

## 13. Strategy UI (inside `/app/commitments`)

**Payment Strategy** panel:

- Current strategy + short why  
- Next priority commitment + reason  
- Ordered list (1…n) for the active currency group  

User may **change strategy**. User may **not** drag-reorder Avalanche/Snowball lists — personal order requires **Manual**.

---

## 14. Projection API

```http
GET /api/v1/organizations/{organization_id}/commitments/strategy
```

(Alias under `/debts/...` acceptable during transition; product path prefers `commitments`.)

```json
{
  "status": "available",
  "strategy": "avalanche",
  "generated_at": "2026-07-25T18:00:00Z",
  "summary": {
    "active_commitments": 4,
    "total_balance": "84500.00",
    "currency": "MXN"
  },
  "next_action": {
    "type": "pay_minimum",
    "commitment_id": "uuid",
    "amount": "1250.00",
    "due_date": "2026-07-28",
    "reason_code": "due_soon"
  },
  "ranking": [
    {
      "position": 1,
      "commitment_id": "uuid",
      "reason_code": "highest_interest_rate"
    }
  ],
  "warnings": []
}
```

Multi-currency: **separate groups** — never one combined total.

`PATCH` (or equivalent) on organization settings updates `debt_strategy` and emits `payment_strategy_changed`.

---

## 15. `DebtStrategyService`

**Does:**

- Filter eligible commitments  
- Detect overdue / due soon  
- Apply hierarchy + strategy sort  
- Emit reason codes + data-gap warnings  
- Build next-action type codes  

**Does not:**

- Create transactions  
- Mutate emotional priorities or debt statuses  
- Compute Safe to Spend  
- Send notifications  

Existing `DebtStrategySimulator` must converge to this contract (add `manual`, hierarchy, eligibility, reason codes, partial data).

---

## 16. Reason codes (API; FE translates)

`overdue` · `due_soon` · `highest_interest_rate` · `lowest_balance` · `manual_priority` · `minimum_payment_required` · `missing_interest_rate` · `missing_payment_schedule` · `defaulted_commitment`

---

## 17. Timeline / observability

**Record:**

- `payment_strategy_changed`  
- `commitment_became_overdue`  
- `commitment_paid_off`  
- `commitment_reopened`  

**Do not record:** `strategy_projection_calculated` (noise).

---

## Acceptance criteria (6.4 design)

- [x] Avalanche / Snowball / Minimum only / Manual defined with hierarchy  
- [x] Org-level strategy; per-debt emotional priority only  
- [x] Recommendations never create movements  
- [x] Incomplete data → `partial` / warnings; no fake 0% APR  
- [x] Currencies never mixed  
- [x] Every rank step has a reason code  
- [x] Cards: settled ≠ permanent paid_off  
- [x] No precise savings promises  
- [x] API + service boundaries specified  

---

## Next

**Sprint 6.5 — Frontend & Implementation Specification** — executable routes, repositories, ViewModels, cache, tests, and commits for end-to-end delivery (includes domain/API alignment still outstanding from earlier maps).
