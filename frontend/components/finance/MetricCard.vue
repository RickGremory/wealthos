<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    amount?: string | null
    currency?: string
    hint?: string
    trendAmount?: string | null
    trendLabel?: string
    status?: 'loading' | 'ready' | 'empty' | 'error' | 'not_configured'
    ctaLabel?: string
    ctaTo?: string
  }>(),
  {
    amount: undefined,
    currency: undefined,
    hint: undefined,
    trendAmount: undefined,
    trendLabel: undefined,
    status: 'ready',
    ctaLabel: undefined,
    ctaTo: undefined,
  },
)
</script>

<template>
  <article class="metric-card" :data-status="status">
    <p class="metric-card__label">{{ label }}</p>

    <template v-if="status === 'loading'">
      <UiSkeleton height="2.4rem" width="70%" />
      <UiSkeleton height="0.85rem" width="50%" style="margin-top: 0.75rem" />
    </template>

    <template v-else-if="status === 'empty'">
      <p class="metric-card__placeholder">Sin datos en esta moneda</p>
      <p v-if="hint" class="metric-card__hint text-muted">{{ hint }}</p>
    </template>

    <template v-else-if="status === 'not_configured'">
      <p class="metric-card__placeholder">Aún no calculado</p>
      <p v-if="hint" class="metric-card__hint text-muted">{{ hint }}</p>
      <NuxtLink v-if="ctaTo" class="metric-card__cta" :to="ctaTo">
        {{ ctaLabel || 'Configurar' }}
      </NuxtLink>
    </template>

    <template v-else>
      <p class="metric-card__value">
        <MoneyValue
          v-if="amount != null && currency"
          :amount="amount"
          :currency="currency"
        />
        <slot v-else />
      </p>

      <p v-if="trendAmount != null && currency" class="metric-card__trend">
        <VarianceIndicator :value="trendAmount" :currency="currency" />
        <span v-if="trendLabel" class="text-muted">{{ trendLabel }}</span>
      </p>

      <div v-if="$slots.details" class="metric-card__details">
        <slot name="details" />
      </div>

      <p v-if="hint" class="metric-card__hint text-muted">{{ hint }}</p>
    </template>
  </article>
</template>

<style scoped>
.metric-card {
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  min-height: 9.5rem;
  display: flex;
  flex-direction: column;
}

.metric-card__label {
  margin: 0 0 var(--space-3);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.metric-card__value {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 2.4vw, 2.15rem);
  font-weight: 650;
  letter-spacing: -0.02em;
  line-height: 1.1;
  color: var(--color-text);
}

.metric-card__placeholder {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.35rem;
  color: var(--color-text-muted);
}

.metric-card__trend {
  margin: var(--space-3) 0 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.85rem;
}

.metric-card__details {
  margin-top: var(--space-4);
  display: grid;
  gap: var(--space-2);
}

.metric-card__hint {
  margin: var(--space-3) 0 0;
  font-size: 0.8rem;
}

.metric-card__cta {
  margin-top: auto;
  padding-top: var(--space-4);
  color: var(--color-primary);
  font-weight: 600;
  font-size: 0.875rem;
  text-decoration: none;
}

.metric-card__cta:hover {
  text-decoration: underline;
}
</style>
