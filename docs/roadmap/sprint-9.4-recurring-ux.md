# Sprint 9.4 — Recurring UX, Calendar & confirmation

**Status:** Accepted  
**Parent:** [Sprint 9](./sprint-9-recurring-engine.md)  
**Contract:** [RFC-005](../rfc/RFC-005-recurring-engine.md)  
**Decision:** [Confirm occurrence → Transaction](../decisions/2026-08-01-recurring-confirm-occurrence.md)  
**Depends on:** [9.1](./sprint-9.1-recurring-domain-model.md) · [9.2](./sprint-9.2-recurrence-generation.md) · [9.3](./sprint-9.3-persistence-lifecycle.md)

---

## Objective

Define how users **create, review, and confirm** recurring movements without confusing an expectation with a real Transaction.

Module question:

> ¿Qué movimientos se repiten y cuáles requieren mi confirmación?

Users must be able to:

- see recurring rules and upcoming occurrences;
- confirm what happened (explicit Transaction);
- skip or reschedule one occurrence;
- change the series from a date (new version);
- feed Planning and Calendar from the same projection;
- register the real movement with minimal friction.

**No application code in this slice** — UX / API read-write surface / FE contracts; build in 9.5 / SPEC.

---

## Navigation

| | |
|--|--|
| Route | `/app/recurring` |
| Detail | `/app/recurring/{rule_id}` |
| Nav label | **Recurrentes** |
| Avoid | “Suscripciones” (too narrow: income, rent, transfers, contributions) |

Suggested nav order: Dashboard · Cuentas · Movimientos · Metas · Obligaciones · Planeación · **Recurrentes** · Calendario · …

---

## Main list IA

```text
Header
Resumen (por moneda)
Requiere atención
Próximas ocurrencias
Reglas recurrentes
Filtros / búsqueda
```

**Header:** Movimientos recurrentes — *Organiza ingresos, pagos y transferencias que se repiten.* · `[Nuevo recurrente]`

### Resumen (always currency-sliced)

| Metric | Meaning |
|--------|---------|
| Ingresos previstos | Expected inflows in horizon |
| Gastos previstos | Expected outflows |
| Próximas ocurrencias | Count in next ~30 days |
| Pendientes de confirmar | Past expected without linked Transaction |

Multiple currencies → groups or selector — **never** a combined FX total (P09).

### Requiere atención

Past occurrences without settlement. Language: **Pendiente de confirmar** — not “Vencido” (reserve “Vencido” for contractual obligations).

Actions: `[Confirmar]` / `[Omitir]` / `[Reprogramar]` (income copy may say Registrar ingreso / No ocurrió / Mover fecha).

### Próximas ocurrencias

Chronological groups (Hoy / Mañana / date). Each row: name, expected amount, direction, date, account, category, certainty, status, rule origin.

### Regla vs ocurrencia

Rule card ≠ next occurrence card.

Rule shows: cadence summary, expected amount, next date, account, status · Ver serie / Editar / Pausar / Archivar.

Externally managed: *Administrado desde Obligaciones* · `[Ver obligación]` — no direct structural edit.

---

## Create flow

1. **Type:** Ingreso / Gasto / Transferencia recurrente  
2. **Cadence templates:** Cada semana · Cada 2 semanas · Cada mes · Cada 3 meses · Cada año · Personalizado  
3. **Form:** name, type, expected amount, currency, frequency, start, optional end, account(s), category, certainty, notes  

Transfers: source ≠ destination; same currency; same org; active accounts; amount > 0.

### Natural language pattern UI

Monthly: *Se repite cada mes* · *El día 15* or *último día* · explicit invalid-date radios (default last day of month).

Weekly: interval + weekday checkboxes · **live preview** of next dates from backend (same generator — never a second FE algorithm).

### Unsaved preview

`POST .../recurring/preview` with draft pattern → dates before persist. Show “Así se programará” with sample occurrences.

---

## Series detail (`/app/recurring/{rule_id}`)

```text
Header · Próxima ocurrencia · Datos · Calendario de ocurrencias
Historial confirmado · Versiones · Pausas · Excepciones · Danger zone
```

Next-occurrence actions: Registrar ahora · Cambiar solo esta · Omitir esta.

### Confirm → Transaction

`Registrar movimiento` opens **existing Transactions** create flow (route query or drawer), prefilled:

- type / amount / account / category / date / description  
- `source_occurrence_key`  
- `related_resource_type = recurring_rule`  
- `related_resource_id`

User may edit amount/date/category before save. After save: occurrence → settled; invalidate planning, calendar, dashboard, accounts, timeline.

**Quick confirm** (fixed amount): still requires an explicit confirmation dialog — no single accidental click that posts a Transaction.

Amount variance (800 → 817): show delta; settle occurrence; optional separate CTA *Actualizar futuras a 817* → new version from chosen date (not automatic).

### Skip / reschedule

- Skip → exception; Planning drops it; series continues.  
- Reschedule → keep original key; change `expected_on`; Planning/Calendar use effective date.

### Edit series

| Choice | Effect |
|--------|--------|
| Solo esta ocurrencia | Exception |
| Esta y las siguientes | New version with `effective_from` |

No “Toda la serie” for structural edits when history exists (descriptive metadata may still patch). Simple vs structural follows [9.3](./sprint-9.3-persistence-lifecycle.md).

Version history is **read-only** in V1 (explain past amounts).

### Pause / resume / end / archive

- Pause: closed or open window; warn no retroactive fill.  
- Resume: close open pause — no backfill.  
- Finalize: set `ends_on` (stop generating).  
- Archive: hide from main list, keep history. **Never** primary “Eliminar”.

---

## Filters & search

Tabs/chips: Todos · Ingresos · Gastos · Transferencias · Activos · Pausados · Finalizados · Archivados · Pendientes de confirmar · Moneda · Cuenta · Categoría · Origen.

Search: name, account, category, related resource. Persist in URL query (`status`, `type`, `currency`, …).

---

## Surfaces outside Recurrentes

| Surface | Behavior |
|---------|----------|
| **Planning** | Same occurrences; exclude settled/skipped/cancelled; include upcoming/due/overdue/(partial) |
| **Calendar** | Occurrences not rules; open → Ver / Registrar / Omitir / Reprogramar via Recurring commands |
| **Dashboard** | Enrich “Próximos movimientos” (3–4 items) — no full new Recurring card required |
| **Timeline** | Material events only: created, paused, resumed, confirmed, skipped, structural amount update — **not** one event per future occurrence |

---

## UI states & permissions

Widgets: `loading` · `ready` · `empty` · `error` · `restricted` · `partial`.

Empty copy: *Todavía no tienes movimientos recurrentes…* · `[Nuevo recurrente]`

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| View | ✓ | ✓ | ✓ | ✓ |
| Create / edit manual / confirm / skip / pause | ✓ | ✓ | ✓ | ✗ |
| Archive | ✓ | ✓ | ✗ | ✗ |
| Edit externally managed | Owner module | Owner module | per that module | ✗ |

Backend remains authority.

---

## API surface (UX-facing refinement of 9.3)

Org-scoped under `/api/v1/organizations/{organization_id}/…`

**Read:** list rules · get rule · list org occurrences (`from`/`to`/`currency`/`status`) · list rule occurrences  

**Write:** create · `PATCH` metadata · `POST .../versions` structural · pauses · resume · exceptions · archive  

**Preview draft:** `POST .../recurring/preview` (unsaved pattern → dates)

**Confirm:** no duplicate Transactions API — deep-link / drawer into Transactions with occurrence context.

Stable error codes for FE mapping: `recurring_rule_managed_externally`, `recurring_version_overlap`, `occurrence_already_settled`, `pause_already_open`, `account_currency_mismatch`, `concurrent_update`, etc. (full list in SPEC).

---

## Frontend contracts

**Repository:** `list` · `get` · `listOccurrences` · `preview` · `create` · `createVersion` · `createException` · `pause` · `resume` · `archive`

**Composables:** `useRecurringRules` · `useRecurringRule` · `useRecurringOccurrences` · `useRecurringPreview` (debounce + cancel in-flight) · `useRecurringMutations` · `useRecurringTransactionPrefill`

**Components (illustrative):** SummaryGrid · AttentionList · OccurrenceList/Card · RuleCard/Form · TypeSelector · PatternEditor · Preview · DetailHeader · VersionHistory · Pause/Exception/Confirmation dialogs · EmptyState

### Cache invalidation

| Event | Invalidate |
|-------|------------|
| Rule create/change | recurring · occurrences · planning · calendar · dashboard upcoming |
| Confirm occurrence | transactions · accounts · recurring · planning · calendar · dashboard · timeline (+ goals/commitments if linked) |
| Skip / reschedule | recurring occurrences · planning · calendar · dashboard upcoming |

---

## E2E matrix (required in 9.5)

1. Create monthly expense → preview → save → Planning + Calendar show it  
2. Confirm with amount variance → settled → dropped from Planning forecast  
3. Skip August → absent from Planning; September continues  
4. Reschedule across months → key stable; effective date moves  
5. Version amount from Sep → Aug keeps old amount  
6. Pause August → no generation; resume → no backfill  

Mobile: primary flows usable on small viewports.

---

## Acceptance criteria (9.4)

- [x] `/app/recurring` + **Recurrentes** nav locked  
- [x] Rules distinguished from occurrences; attention = Pendiente de confirmar  
- [x] Create inflow/outflow/transfer with natural pattern + backend preview  
- [x] Confirm via Transactions prefill + explicit dialog; never auto-post  
- [x] Skip / reschedule / version-from-date / pause-resume / archive  
- [x] Externally managed redirects to owner  
- [x] Planning & Calendar share occurrences; currency sliced  
- [x] FE repository/composables/invalidation + E2E matrix defined  

*(Design acceptance; implementation in 9.5 / SPEC.)*

---

## Main decision of 9.4

Confirmation is always an **explicit Transaction create** (prefilled). Recurring never invents ledger rows; UI language keeps expectations vs facts separate.

## Next

**Sprint 9.5 — Implementation SPEC & hardening:** DTOs, migrations, definitive endpoints, permissions, performance, observability, PR order to ship Recurring end-to-end.
