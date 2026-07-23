# ADR-002: Nuxt for the frontend

- **Status:** accepted
- **Date:** 2026-07-23
- **Deciders:** WealthOS core

## Context

WealthOS needs a web client for independent professionals: dashboards, goals, cashflow, and settings. The frontend should support SSR/SSG where useful, clear routing, and a modern Vue ecosystem.

## Decision

Use **Nuxt** (Vue) as the primary web frontend framework.

## Consequences

### Positive
- File-based routing and conventions reduce boilerplate
- SSR/hybrid rendering options for performance and SEO (marketing + app)
- Strong DX with Vue 3 / composables

### Negative / trade-offs
- Nuxt-specific patterns to learn and maintain
- Must keep financial truth on the backend — UI only reflects it
- Mobile/native clients, if needed later, will be separate surfaces

## Alternatives considered
- Next.js (React) — large ecosystem; rejected to standardize on Vue/Nuxt
- Plain Vue SPA — simpler deploy; weaker SSR and convention story
- Remix / SvelteKit — solid options; less alignment with chosen Vue path
