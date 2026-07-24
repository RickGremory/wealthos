<template>
  <div class="layout-legal">
    <header class="layout-legal__header">
      <NuxtLink to="/" class="layout-legal__brand">
        WealthOS
      </NuxtLink>
      <nav class="layout-legal__nav">
        <NuxtLink to="/legal">Legal</NuxtLink>
        <NuxtLink to="/login">Iniciar sesión</NuxtLink>
      </nav>
    </header>
    <main class="layout-legal__main">
      <slot />
    </main>
    <footer class="layout-legal__footer">
      <NuxtLink to="/legal/cookies">Cookies</NuxtLink>
      <span aria-hidden="true">·</span>
      <NuxtLink to="/legal/privacy">Privacidad</NuxtLink>
      <span aria-hidden="true">·</span>
      <NuxtLink to="/legal/terms">Términos</NuxtLink>
    </footer>
  </div>
</template>

<style scoped>
.layout-legal {
  min-height: 100vh;
  min-height: 100dvh;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(180deg, rgba(11, 61, 58, 0.06), transparent 28%),
    var(--color-bg, #f8fafc);
  color: var(--color-text, #0f172a);
}

.layout-legal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4, 1rem);
  padding: var(--space-4, 1rem) var(--space-5, 1.25rem);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  min-width: 0;
}

.layout-legal__brand {
  font-family: var(--font-display, Georgia, serif);
  font-size: 1.5rem;
  font-weight: 700;
  color: inherit;
  text-decoration: none;
}

.layout-legal__nav {
  display: flex;
  gap: var(--space-4, 1rem);
  flex-wrap: wrap;
  font-size: 0.9rem;
}

.layout-legal__nav a {
  color: var(--color-slate-700, #334155);
}

.layout-legal__main {
  flex: 1;
  width: 100%;
  max-width: 44rem;
  margin: 0 auto;
  padding: var(--space-6, 1.5rem) var(--space-4, 1rem) var(--space-8, 2rem);
  min-width: 0;
}

.layout-legal__footer {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2, 0.5rem);
  justify-content: center;
  padding: var(--space-4, 1rem);
  font-size: 0.85rem;
  color: var(--color-slate-600, #475569);
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.layout-legal__footer a {
  color: inherit;
}

@media print {
  .layout-legal__header,
  .layout-legal__footer,
  .layout-legal__nav {
    display: none;
  }

  .layout-legal {
    background: white;
  }

  .layout-legal__main {
    max-width: none;
    padding: 0;
  }
}
</style>
