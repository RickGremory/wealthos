<script setup lang="ts">
defineProps<{
  currencies: string[]
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div
    v-if="currencies.length"
    class="currency-selector"
    role="group"
    aria-label="Moneda del dashboard"
    data-testid="dashboard-currency-selector"
  >
    <span class="currency-selector__label">Moneda</span>
    <div class="currency-selector__chips">
      <button
        v-for="code in currencies"
        :key="code"
        type="button"
        class="currency-selector__chip"
        :data-active="modelValue === code"
        :aria-pressed="modelValue === code"
        @click="emit('update:modelValue', code)"
      >
        {{ code }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.currency-selector {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0.35rem 0.45rem 0.35rem 0.75rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-strong, var(--color-border));
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
}

.currency-selector__label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.currency-selector__chips {
  display: inline-flex;
  gap: 0.25rem;
}

.currency-selector__chip {
  min-width: 3.5rem;
  min-height: 2.35rem;
  padding: 0.4rem 0.85rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-text-muted);
  font-weight: 750;
  font-size: 0.88rem;
  letter-spacing: 0.04em;
  cursor: pointer;
}

.currency-selector__chip[data-active='true'] {
  border-color: var(--color-primary);
  background: rgba(11, 61, 58, 0.1);
  color: var(--color-primary);
}

.currency-selector__chip:focus-visible {
  outline: 2px solid var(--color-teal-700);
  outline-offset: 2px;
}
</style>
