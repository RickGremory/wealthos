<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'teal'
  }>(),
  {
    tone: 'neutral',
  },
)
</script>

<template>
  <span class="ui-badge" :class="`ui-badge--${tone}`">
    <slot />
  </span>
</template>

<style scoped>
.ui-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.ui-badge--neutral {
  background: var(--color-slate-200);
  color: var(--color-slate-800);
}

.ui-badge--success {
  background: var(--color-success-muted);
  color: var(--color-success);
}

.ui-badge--warning {
  background: var(--color-warning-muted);
  color: var(--color-warning);
}

.ui-badge--danger {
  background: var(--color-danger-muted);
  color: var(--color-danger);
}

.ui-badge--teal {
  background: var(--color-teal-100);
  color: var(--color-teal-900);
}
</style>
