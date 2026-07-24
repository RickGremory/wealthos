<script setup lang="ts">
defineProps<{
  caption?: string
}>()
</script>

<template>
  <div class="ui-table-wrap">
    <table class="ui-table">
      <caption v-if="caption" class="sr-only">{{ caption }}</caption>
      <thead v-if="$slots.head">
        <slot name="head" />
      </thead>
      <tbody>
        <slot />
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.ui-table-wrap {
  width: 100%;
  overflow: auto;
}

.ui-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.ui-table :deep(th),
.ui-table :deep(td) {
  text-align: left;
  padding: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.ui-table :deep(th) {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  font-weight: 600;
}
</style>
