<script setup lang="ts">
import type { CommitmentSummaryView } from '~/types/commitments'

defineProps<{
  summary: CommitmentSummaryView
  loading?: boolean
  error?: string | null
}>()
</script>

<template>
  <section
    class="commitment-summary"
    aria-label="Resumen de obligaciones"
    data-testid="commitment-summary"
  >
    <div v-if="loading" class="commitment-summary__grid">
      <UiSkeleton height="5.5rem" />
      <UiSkeleton height="5.5rem" />
      <UiSkeleton height="5.5rem" />
      <UiSkeleton height="5.5rem" />
    </div>
    <UiAlert
      v-else-if="error"
      tone="warning"
      title="Resumen parcial no disponible"
      data-testid="commitment-summary-error"
    >
      {{ error }}
    </UiAlert>
    <div v-else class="commitment-summary__grid">
      <div class="commitment-summary__metric">
        <span class="commitment-summary__label">Activas</span>
        <strong class="commitment-summary__value">{{ summary.activeCommitments }}</strong>
      </div>
      <div class="commitment-summary__metric">
        <span class="commitment-summary__label">Requieren atención</span>
        <strong class="commitment-summary__value">
          {{ summary.commitmentsNeedingAttention }}
        </strong>
      </div>
      <div class="commitment-summary__metric">
        <span class="commitment-summary__label">Próximo pago</span>
        <strong
          class="commitment-summary__value commitment-summary__value--name"
          :title="summary.nextDue?.name || undefined"
        >
          <template v-if="summary.nextDue">
            {{ summary.nextDue.name }}
            <span class="text-muted" style="font-weight: 500; font-size: 0.85rem">
              · {{ summary.nextDue.daysUntilDue }}d
            </span>
          </template>
          <template v-else>—</template>
        </strong>
      </div>
      <div class="commitment-summary__metric">
        <span class="commitment-summary__label">Totales por moneda</span>
        <strong class="commitment-summary__value commitment-summary__groups">
          <template v-if="summary.groups.length">
            <span
              v-for="group in summary.groups"
              :key="group.currency"
              class="commitment-summary__group"
            >
              <CurrencyBadge :currency="group.currency" />
              <MoneyValue
                :amount="group.totalDebt"
                :currency="group.currency"
                :emphasize-sign="false"
              />
            </span>
          </template>
          <template v-else>—</template>
        </strong>
      </div>
    </div>
  </section>
</template>

<style scoped>
.commitment-summary__grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (min-width: 900px) {
  .commitment-summary__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.commitment-summary__metric {
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  display: grid;
  gap: var(--space-1);
}

.commitment-summary__label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.commitment-summary__value {
  font-size: clamp(0.95rem, 3.6vw, 1.2rem);
  color: var(--color-teal-900);
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}

.commitment-summary__value--name {
  font-size: clamp(0.9rem, 3.2vw, 1rem);
}

.commitment-summary__groups {
  display: grid;
  gap: var(--space-2);
  font-size: 0.95rem;
}

.commitment-summary__group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}
</style>
