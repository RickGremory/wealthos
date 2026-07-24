<script setup lang="ts">
withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    size?: 'sm' | 'md'
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    block?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    type: 'button',
    disabled: false,
    block: false,
  },
)
</script>

<template>
  <button
    class="ui-button"
    :class="[
      `ui-button--${variant}`,
      `ui-button--${size}`,
      { 'ui-button--block': block },
    ]"
    :type="type"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<style scoped>
.ui-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  font-weight: 600;
  cursor: pointer;
  transition: background 140ms ease, border-color 140ms ease, color 140ms ease;
}

.ui-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.ui-button--sm {
  padding: 0.35rem 0.7rem;
  font-size: 0.8125rem;
}

.ui-button--md {
  padding: 0.55rem 1rem;
  font-size: 0.9rem;
}

.ui-button--block {
  width: 100%;
}

.ui-button--primary {
  background: var(--color-primary);
  color: var(--color-text-inverse);
}

.ui-button--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.ui-button--secondary {
  background: var(--color-surface);
  border-color: var(--color-border-strong);
  color: var(--color-ink);
}

.ui-button--secondary:hover:not(:disabled) {
  background: var(--color-surface-muted);
}

.ui-button--ghost {
  background: transparent;
  color: var(--color-slate-700);
}

.ui-button--ghost:hover:not(:disabled) {
  background: rgba(15, 23, 42, 0.05);
}

.ui-button--danger {
  background: var(--color-danger);
  color: #fff;
}

.ui-button--danger:hover:not(:disabled) {
  filter: brightness(0.95);
}
</style>
