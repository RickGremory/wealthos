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
    <span class="category-badge__name">{{ name }}</span>
    <UiBadge v-if="isSystem" class="category-badge__system" tone="neutral">
      Sistema
    </UiBadge>
  </span>
</template>

<style scoped>
.category-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  max-width: 100%;
  font-weight: 600;
}

.category-badge__swatch {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 999px;
  flex-shrink: 0;
}

.category-badge__icon {
  flex-shrink: 0;
  font-size: 0.95rem;
}

.category-badge__name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-badge__system {
  flex-shrink: 0;
}
</style>
