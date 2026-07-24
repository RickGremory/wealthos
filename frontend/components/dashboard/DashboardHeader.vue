<script setup lang="ts">
defineProps<{
  greeting: string
  subtitle: string
}>()
</script>

<template>
  <header class="dashboard-header">
    <div class="stack-sm">
      <h1 class="dashboard-header__title" data-testid="page-title">
        {{ greeting }}
      </h1>
      <p class="dashboard-header__subtitle text-muted">
        {{ subtitle }}
      </p>
    </div>
    <div class="dashboard-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.dashboard-header__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3vw, 2.25rem);
  font-weight: 650;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.dashboard-header__subtitle {
  margin: 0;
  font-size: 0.98rem;
}

.dashboard-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: flex-end;
}

@media (max-width: 700px) {
  .dashboard-header {
    flex-direction: column;
  }

  .dashboard-header__actions {
    width: 100%;
  }
}
</style>
