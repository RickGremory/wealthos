<template>
  <div class="layout-auth">
    <div class="layout-auth__atmosphere" aria-hidden="true" />
    <div class="layout-auth__content">
      <header class="layout-auth__brand">
        <p class="layout-auth__logo">WealthOS</p>
        <p class="layout-auth__tagline">Tu sistema operativo financiero</p>
      </header>
      <main class="layout-auth__main">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout-auth {
  position: relative;
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  overflow-x: hidden;
  overflow-y: auto;
}

.layout-auth__atmosphere {
  position: absolute;
  inset: 0;
  background: var(--auth-gradient);
  animation: auth-shift 18s ease-in-out infinite alternate;
  /* Avoid scaled background causing page overflow */
  transform-origin: center;
}

.layout-auth__content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 26rem;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.layout-auth__brand {
  text-align: center;
  color: var(--color-text-inverse);
  min-width: 0;
  padding-inline: var(--space-2);
}

.layout-auth__logo {
  font-family: var(--font-display);
  font-size: clamp(2.1rem, 8vw, 3.25rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  animation: brand-in 700ms ease-out both;
}

.layout-auth__tagline {
  margin: var(--space-2) 0 0;
  color: rgba(248, 250, 252, 0.78);
  font-size: 0.95rem;
  overflow-wrap: anywhere;
  animation: brand-in 900ms ease-out both;
}

.layout-auth__main {
  min-width: 0;
  width: 100%;
  animation: panel-in 650ms ease-out both;
}

.layout-auth__main :deep(.ui-card) {
  width: 100%;
  max-width: 100%;
}

@media (min-width: 480px) {
  .layout-auth {
    padding: var(--space-6);
  }

  .layout-auth__content {
    gap: var(--space-8);
  }
}

@keyframes auth-shift {
  from {
    filter: hue-rotate(0deg) saturate(1);
  }
  to {
    filter: hue-rotate(-8deg) saturate(1.08);
  }
}

@keyframes brand-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
