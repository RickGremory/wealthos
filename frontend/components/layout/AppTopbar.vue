<script setup lang="ts">
defineEmits<{ toggleNav: [] }>()

const auth = useAuthStore()
const preferences = usePreferencesStore()

async function onLogout() {
  await auth.logout()
}
</script>

<template>
  <header class="topbar">
    <div class="cluster">
      <button
        type="button"
        class="topbar__menu"
        aria-label="Abrir menú"
        @click="$emit('toggleNav')"
      >
        Menú
      </button>
      <p class="topbar__user text-muted">
        {{ auth.user?.displayName || auth.user?.email || 'Sesión activa' }}
      </p>
    </div>

    <div class="cluster-sm">
      <UiButton
        variant="ghost"
        size="sm"
        type="button"
        @click="preferences.toggleHideBalances()"
      >
        {{ preferences.hideBalances ? 'Mostrar montos' : 'Ocultar montos' }}
      </UiButton>
      <UiButton
        variant="secondary"
        size="sm"
        type="button"
        data-testid="logout-button"
        @click="onLogout"
      >
        Salir
      </UiButton>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: var(--topbar-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: 0 var(--space-6);
  border-bottom: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 20;
}

.topbar__menu {
  display: none;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
}

.topbar__user {
  margin: 0;
  font-size: 0.875rem;
}

@media (max-width: 900px) {
  .topbar__menu {
    display: inline-flex;
  }
}
</style>
