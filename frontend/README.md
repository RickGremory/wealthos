# WealthOS Frontend

Fundación Nuxt 3 (Sprint 5.0) para WealthOS: autenticación, shell de app, cliente API tipado y capas Page → Composable → Repository → API.

## Stack

- **Nuxt 3** + Vue 3 + TypeScript (strict)
- **Pinia** para estado (auth, organización, toasts, preferencias)
- **ofetch** vía cliente propio (`lib/api`)
- **Vitest** (unit) + **Playwright** (e2e)
- OpenAPI: `openapi/wealthos.json` → `types/api.generated.ts`

## Scripts

```bash
npm run dev              # http://localhost:3000
npm run build
npm run preview
npm run lint
npm run typecheck
npm run generate:api     # regenera types/api.generated.ts
npm run test             # vitest unit
npm run test:e2e         # playwright (levanta dev server)
```

## Variables de entorno

Copia `.env.example` a `.env`:

| Variable | Descripción |
|----------|-------------|
| `NUXT_PUBLIC_API_BASE_URL` | Base del API (default `http://127.0.0.1:8000/api/v1`) |
| `NUXT_PUBLIC_FEATURE_FLAGS` | JSON de flags (`planning`, `taxes`, `debts`, `goals`) |

## Arquitectura

```
Page / Component
  → Composable (useMoney, useToast, …)
  → Repository (auth / accounts / organizations)
  → ApiClient (Bearer, X-Request-Id, X-Organization-Id)
  → Backend FastAPI
```

- **Stores**: token en cookie `wealthos_access_token` (SSR-friendly; httpOnly vendrá después vía BFF). Org activa en `wealthos_organization_id`.
- **Middleware**: `auth`, `guest`, `organization` en rutas `/app/*`.
- **Layouts**: `auth` (branding), `app` (AppShell), `default`.
- **Dinero**: montos como `string`; `formatMoney` solo para display — no usar `Number` para aritmética financiera.

## Diseño

Paleta slate + teal/ink, tipografía Fraunces (display) + Manrope (UI), atmósfera con gradiente en layout de auth.

## Estructura clave

```
assets/css/          tokens, main, utilities
lib/api/             client, errors, types
repositories/        auth, accounts, organizations
stores/              auth, organization, notifications, preferences
composables/         api, money, date, flags, toast, nav
components/          layout, ui, finance, feedback
pages/               login, register, onboarding, app/*
tests/unit|e2e/
```
