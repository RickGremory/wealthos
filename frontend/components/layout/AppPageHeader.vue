<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <header class="page-header">
    <div class="stack-sm">
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

.page-header__title {
  font-size: clamp(1.5rem, 2.5vw, 1.85rem);
}

.page-header__desc {
  font-size: 0.95rem;
}

.page-header__actions {
  flex-shrink: 0;
}
</style>
