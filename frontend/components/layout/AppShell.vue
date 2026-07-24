<script setup lang="ts">
const mobileOpen = ref(false)

function closeMobile() {
  mobileOpen.value = false
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

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .app-shell__sidebar {
    display: none;
  }
}
</style>
