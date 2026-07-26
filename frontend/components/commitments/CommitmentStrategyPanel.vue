<script setup lang="ts">
import type { CommitmentStrategyView, PaymentStrategy } from '~/types/commitments'
import {
  getPaymentStrategyDescription,
  getPaymentStrategyLabel,
  getStrategyReasonLabel,
  PAYMENT_STRATEGY_OPTIONS,
} from '~/utils/commitment-strategy'

const props = defineProps<{
  strategy: CommitmentStrategyView | null
  loading?: boolean
  error?: string | null
  canManage?: boolean
  updating?: boolean
}>()

const emit = defineEmits<{
  change: [strategy: PaymentStrategy]
  open: [commitmentId: string]
}>()

const selected = computed({
  get: () => props.strategy?.strategy ?? 'avalanche',
  set: (value: PaymentStrategy) => emit('change', value),
})

const priorityName = computed(() => {
  const view = props.strategy
  if (!view?.nextAction?.commitmentId) return 'Ver obligación'
  return (
    view.ranking.find(r => r.commitmentId === view.nextAction?.commitmentId)?.name
    || 'Ver obligación'
  )
})

function openPriority() {
  const id = props.strategy?.nextAction?.commitmentId
  if (id) emit('open', id)
}
</script>

<template>
  <UiCard title="Estrategia de pago" data-testid="commitment-strategy-panel">
    <div v-if="loading" class="stack">
      <UiSkeleton height="4rem" />
      <UiSkeleton height="6rem" />
    </div>
    <UiAlert v-else-if="error" tone="warning" title="No se pudo cargar la estrategia">
      {{ error }}
    </UiAlert>
    <div v-else-if="strategy" class="strategy stack">
      <div class="strategy__controls">
        <label class="strategy__label" for="payment-strategy">Estrategia</label>
        <UiSelect
          id="payment-strategy"
          v-model="selected"
          :disabled="!canManage || updating"
          :options="PAYMENT_STRATEGY_OPTIONS.map(o => ({ label: o.label, value: o.value }))"
        />
        <p class="text-muted strategy__desc">
          {{ getPaymentStrategyDescription(strategy.strategy) }}
        </p>
      </div>

      <UiAlert
        v-for="(warning, idx) in strategy.warnings"
        :key="idx"
        tone="warning"
        title="Datos parciales"
      >
        {{ warning }}
      </UiAlert>

      <div v-if="strategy.nextAction?.commitmentId" class="strategy__next">
        <span class="text-muted">Prioridad ahora</span>
        <button type="button" class="strategy__link" @click="openPriority">
          {{ priorityName }}
        </button>
        <span class="text-muted">
          · {{ getStrategyReasonLabel(strategy.nextAction.reasonCode) }}
        </span>
      </div>

      <ol v-if="strategy.ranking.length" class="strategy__ranking">
        <li
          v-for="item in strategy.ranking"
          :key="item.commitmentId"
          class="strategy__rank-item"
        >
          <button type="button" class="strategy__link" @click="emit('open', item.commitmentId)">
            {{ item.position }}. {{ item.name }}
          </button>
          <span class="text-muted">{{ getStrategyReasonLabel(item.reasonCode) }}</span>
        </li>
      </ol>
      <p v-else class="text-muted">
        {{ getPaymentStrategyLabel(strategy.strategy) }}:
        no hay suficientes obligaciones activas para un ranking.
      </p>
    </div>
  </UiCard>
</template>

<style scoped>
.strategy__label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: var(--space-2);
}

.strategy__desc {
  margin: var(--space-2) 0 0;
  font-size: 0.85rem;
}

.strategy__next {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: baseline;
  font-size: 0.9rem;
}

.strategy__ranking {
  margin: 0;
  padding-left: 1.1rem;
  display: grid;
  gap: var(--space-2);
}

.strategy__rank-item {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: baseline;
}

.strategy__link {
  border: 0;
  background: transparent;
  color: var(--color-teal-800);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  text-align: left;
}

.strategy__link:hover {
  text-decoration: underline;
}
</style>
