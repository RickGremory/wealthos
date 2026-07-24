<script setup lang="ts">
const mobileOpen = ref(false)
const route = useRoute()
const composer = useTransactionComposerStore()
const { canWrite } = useOrganizationPermissions()

const showFab = computed(() =>
  canWrite.value && route.path.startsWith('/app'),
)

function closeMobile() {
  mobileOpen.value = false
}

function openNewTransaction() {
  composer.openCreate('expense')
}
</script>

<template>
  <div class="app-shell" :class="{ 'app-shell--nav-open': mobileOpen }">
    <AppSidebar class="app-shell__sidebar" @navigate="closeMobile" />
    <div class="app-shell__main">
      <AppTopbar @toggle-nav="mobileOpen = !mobileOpen" />
      <MobileNav v-if="mobileOpen" @close="closeMobile" />
      <main class="app-shell__content">
        <slot />
      </main>
    </div>

    <button
      v-if="showFab"
      type="button"
      class="app-shell__fab"
      aria-label="Nueva transacción"
      data-testid="mobile-new-transaction-fab"
      @click="openNewTransaction"
    >
      +
    </button>

    <QuickTransactionDrawer />
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  background:
    radial-gradient(ellipse 60% 40% at 100% 0%, rgba(19, 111, 105, 0.08), transparent 55%),
    var(--color-bg);
}

.app-shell__main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.app-shell__content {
  flex: 1;
  padding: var(--space-6);
  max-width: 72rem;
  width: 100%;
  margin: 0 auto;
}

.app-shell__fab {
  display: none;
  position: fixed;
  right: 1.25rem;
  bottom: 1.25rem;
  width: 3.25rem;
  height: 3.25rem;
  border: 0;
  border-radius: 999px;
  background: var(--color-primary);
  color: white;
  font-size: 1.75rem;
  line-height: 1;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  z-index: 30;
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .app-shell__sidebar {
    display: none;
  }

  .app-shell__content {
    padding: var(--space-4);
    padding-bottom: calc(var(--space-6) + 4rem);
    overflow-x: hidden;
  }

  .app-shell__fab {
    display: inline-grid;
    place-items: center;
  }
}
</style>
