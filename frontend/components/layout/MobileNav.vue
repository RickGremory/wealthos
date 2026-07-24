<script setup lang="ts">
defineEmits<{ close: [] }>()

const route = useRoute()
const { groups } = useAppNav()

function isActive(to: string) {
  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <div class="mobile-nav" role="dialog" aria-label="Navegación móvil">
    <div class="mobile-nav__panel">
      <div class="cluster" style="justify-content: space-between">
        <strong class="text-display">WealthOS</strong>
        <UiButton variant="ghost" size="sm" type="button" @click="$emit('close')">
          Cerrar
        </UiButton>
      </div>

      <nav class="stack">
        <section v-for="group in groups" :key="group.id" class="stack-sm">
          <h2 class="mobile-nav__label">{{ group.label }}</h2>
          <NuxtLink
            v-for="item in group.items"
            :key="item.to"
            :to="item.to"
            class="mobile-nav__link"
            :class="{ 'mobile-nav__link--active': isActive(item.to) }"
            @click="$emit('close')"
          >
            {{ item.label }}
          </NuxtLink>
        </section>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.mobile-nav {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(10, 22, 40, 0.45);
}

.mobile-nav__panel {
  width: min(100%, 20rem);
  height: 100%;
  background: var(--color-ink);
  color: var(--color-text-inverse);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  animation: slide-in 200ms ease-out;
}

.mobile-nav__label {
  font-family: var(--font-ui);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(248, 250, 252, 0.45);
  margin: 0;
}

.mobile-nav__link {
  color: rgba(248, 250, 252, 0.85);
  text-decoration: none;
  padding: var(--space-2) 0;
  font-weight: 500;
}

.mobile-nav__link--active {
  color: var(--color-teal-100);
}

@keyframes slide-in {
  from {
    transform: translateX(-12px);
    opacity: 0.6;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (min-width: 901px) {
  .mobile-nav {
    display: none;
  }
}
</style>
