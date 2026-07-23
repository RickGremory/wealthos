# Decision Log

Chronological record of meaningful product and technical decisions.

Format: newest first.

---

## Template

### YYYY-MM-DD — Short title
- **Status:** proposed | accepted | superseded | deprecated
- **Context:** What forced the decision?
- **Decision:** What did we choose?
- **Consequences:** What becomes easier / harder?
- **Alternatives considered:** What else was on the table?

---

## Entries

### 2026-07-23 — Docs layout by concern
- **Status:** accepted
- **Context:** Flat `docs/*.md` did not match the intended documentation IA.
- **Decision:** Organize docs into `product/`, `architecture/`, `engineering/`, `roadmap/`, `api/`, `database/`, `decisions/`, plus `adr/`.
- **Consequences:** Clearer navigation; numbered docs keep their filenames inside topic folders.
- **Alternatives considered:** Keep flat docs; single `book/` only.

### 2026-07-23 — Initial documentation spine
- **Status:** accepted
- **Context:** Repo scaffold exists; product and engineering need a shared written baseline.
- **Decision:** Establish numbered docs `00`–`10` as the core narrative (manifesto → vision → principles → structure → roadmap → standards → tests).
- **Consequences:** Contributors and agents have a single place to start; deeper specs still live in `specs/`.
- **Alternatives considered:** Keep only README; defer docs until code exists.
