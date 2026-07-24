<script setup lang="ts">
defineProps<{
  name: string
  color?: string
  icon?: string
  isSystem?: boolean
}>()
</script>

<template>
  <span class="category-badge">
    <span
      class="category-badge__swatch"
      :style="{ background: color || 'var(--color-teal-500)' }"
      aria-hidden="true"
    />
    <span v-if="icon" class="category-badge__icon" aria-hidden="true">{{ icon }}</span>
    <span>{{ name }}</span>
    <UiBadge v-if="isSystem" tone="neutral">Sistema</UiBadge>
  </span>
</template>

<style scoped>
.category-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: 600;
}

.category-badge__swatch {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 999px;
  flex-shrink: 0;
}

.category-badge__icon {
  font-size: 0.95rem;
}
</style>
