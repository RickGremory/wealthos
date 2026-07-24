<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  backTo?: string
  backLabel?: string
}>()
</script>

<template>
  <header class="page-header">
    <div class="stack-sm">
      <NuxtLink
        v-if="backTo"
        :to="backTo"
        class="page-header__back"
        data-testid="page-back-link"
      >
        {{ backLabel || 'Volver' }}
      </NuxtLink>
      <h1 class="page-header__title" data-testid="page-title">{{ title }}</h1>
      <p v-if="description" class="page-header__desc text-muted">
        {{ description }}
      </p>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.page-header__back {
  display: inline-flex;
  width: fit-content;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
}

.page-header__back:hover {
  color: var(--color-primary);
}

.page-header__title {
  font-size: clamp(1.5rem, 2.5vw, 1.85rem);
}

.page-header__desc {
  font-size: 0.95rem;
}

.page-header__actions {
  flex-shrink: 0;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    margin-bottom: var(--space-4);
  }

  .page-header__title {
    font-size: 1.45rem;
    overflow-wrap: anywhere;
  }

  .page-header__actions {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2);
  }
}
</style>
