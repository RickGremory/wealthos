<script setup lang="ts">
withDefaults(
  defineProps<{
    tone?: 'info' | 'success' | 'warning' | 'danger'
    title?: string
  }>(),
  {
    tone: 'info',
    title: undefined,
  },
)
</script>

<template>
  <div class="ui-alert" :class="`ui-alert--${tone}`" role="alert">
    <strong v-if="title" class="ui-alert__title">{{ title }}</strong>
    <div class="ui-alert__body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.ui-alert {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface-muted);
}

.ui-alert__title {
  display: block;
  margin-bottom: var(--space-1);
}

.ui-alert--info {
  background: #eef6ff;
  border-color: #b2ddff;
}

.ui-alert--success {
  background: var(--color-success-muted);
  border-color: #abefc6;
}

.ui-alert--warning {
  background: var(--color-warning-muted);
  border-color: #fedf89;
}

.ui-alert--danger {
  background: var(--color-danger-muted);
  border-color: #fecdca;
}
</style>
