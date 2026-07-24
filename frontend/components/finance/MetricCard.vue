<script setup lang="ts">
defineProps<{
  label: string
  amount?: string | null
  currency?: string
  hint?: string
}>()
</script>

<template>
  <article class="metric-card">
    <p class="metric-card__label">{{ label }}</p>
    <p class="metric-card__value">
      <MoneyValue
        v-if="amount != null && currency"
        :amount="amount"
        :currency="currency"
      />
      <slot v-else />
    </p>
    <p v-if="hint" class="metric-card__hint text-muted">{{ hint }}</p>
  </article>
</template>

<style scoped>
.metric-card {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.metric-card__label {
  margin: 0 0 var(--space-2);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-card__value {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.5rem;
}

.metric-card__hint {
  margin: var(--space-2) 0 0;
  font-size: 0.8rem;
}
</style>
