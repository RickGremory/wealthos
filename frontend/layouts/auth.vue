<template>
  <div class="layout-auth">
    <div class="layout-auth__atmosphere" aria-hidden="true" />
    <div class="layout-auth__content">
      <header class="layout-auth__brand">
        <p class="layout-auth__logo">WealthOS</p>
        <p class="layout-auth__tagline">Claridad financiera, sin ruido</p>
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
  display: grid;
  place-items: center;
  padding: var(--space-6);
  overflow: hidden;
}

.layout-auth__atmosphere {
  position: absolute;
  inset: 0;
  background: var(--auth-gradient);
  animation: auth-shift 18s ease-in-out infinite alternate;
}

.layout-auth__content {
  position: relative;
  z-index: 1;
  width: min(100%, 26rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.layout-auth__brand {
  text-align: center;
  color: var(--color-text-inverse);
}

.layout-auth__logo {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 6vw, 3.25rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  animation: brand-in 700ms ease-out both;
}

.layout-auth__tagline {
  margin: var(--space-2) 0 0;
  color: rgba(248, 250, 252, 0.78);
  font-size: 0.95rem;
  animation: brand-in 900ms ease-out both;
}

.layout-auth__main {
  animation: panel-in 650ms ease-out both;
}

@keyframes auth-shift {
  from {
    filter: hue-rotate(0deg) saturate(1);
    transform: scale(1);
  }
  to {
    filter: hue-rotate(-8deg) saturate(1.08);
    transform: scale(1.04);
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
