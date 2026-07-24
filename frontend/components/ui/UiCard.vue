<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string
    padded?: boolean
  }>(),
  {
    title: undefined,
    padded: true,
  },
)
</script>

<template>
  <section class="ui-card" :class="{ 'ui-card--padded': padded }">
    <header v-if="title || $slots.header" class="ui-card__header">
      <h2 v-if="title" class="ui-card__title">{{ title }}</h2>
      <slot name="header" />
    </header>
    <div class="ui-card__body">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="ui-card__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<style scoped>
.ui-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.ui-card--padded {
  padding: var(--space-5);
}

.ui-card__header {
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.ui-card__title {
  font-size: 1.05rem;
  margin: 0;
}

.ui-card__body {
  min-width: 0;
}

.ui-card__footer {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-border);
}
</style>
