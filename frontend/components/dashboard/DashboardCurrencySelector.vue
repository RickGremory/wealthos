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
    v-if="currencies.length > 1"
    class="currency-selector"
    role="group"
    aria-label="Moneda del dashboard"
  >
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
</template>

<style scoped>
.currency-selector {
  display: inline-flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.currency-selector__chip {
  min-width: 3.25rem;
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
  cursor: pointer;
}

.currency-selector__chip[data-active='true'] {
  border-color: var(--color-primary);
  background: rgba(11, 61, 58, 0.08);
  color: var(--color-primary);
}
</style>
