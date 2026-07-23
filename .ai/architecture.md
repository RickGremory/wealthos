# WealthOS — Architecture

System design notes for AI agents and contributors.

## Status
Scaffold only. Architecture decisions are pending.

## Intended layers
- **Frontend** — user-facing clients
- **Backend** — domain logic and APIs
- **Infrastructure** — runtime, data stores, networking, CI/CD

## Principles (draft)
- Clear bounded contexts over a single monolith dump
- Explicit contracts between frontend and backend
- Secrets and environment config stay out of source control
