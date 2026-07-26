<script setup lang="ts">
import type { CommitmentNextActionView } from '~/types/commitments'
import {
  describeNextAction,
  getNextActionTitle,
  getNextActionTone,
} from '~/utils/commitment-next-action'

const props = defineProps<{
  action: CommitmentNextActionView | null
  currency?: string
  compact?: boolean
  canPay?: boolean
}>()

const emit = defineEmits<{
  pay: []
}>()

const title = computed(() =>
  props.action ? getNextActionTitle(props.action.type) : 'Siguiente paso',
)
const tone = computed(() =>
  props.action ? getNextActionTone(props.action.type) : 'neutral',
)

const showPay = computed(() => {
  if (!props.canPay || !props.action) return false
  return ['pay_overdue', 'pay_minimum', 'pay_priority_debt'].includes(props.action.type)
})
</script>

<template>
  <div
    class="next-action"
    :class="{ 'next-action--compact': compact }"
    data-testid="commitment-next-action"
  >
    <div class="next-action__head">
      <UiBadge :tone="tone">{{ title }}</UiBadge>
      <p class="next-action__desc text-muted">
        {{ describeNextAction(action) }}
      </p>
    </div>
    <div v-if="action?.amount && currency" class="next-action__amount">
      <MoneyValue :amount="action.amount" :currency="currency" :emphasize-sign="false" />
      <span v-if="action.dueDate" class="text-muted"> · {{ action.dueDate }}</span>
    </div>
    <div v-if="showPay && !compact" class="next-action__cta">
      <UiButton type="button" data-testid="commitment-next-action-pay" @click="emit('pay')">
        Registrar pago
      </UiButton>
    </div>
  </div>
</template>

<style scoped>
.next-action {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.next-action--compact {
  padding: 0;
  border: 0;
  background: transparent;
}

.next-action__head {
  display: grid;
  gap: var(--space-1);
}

.next-action__desc {
  margin: 0;
  font-size: 0.85rem;
}

.next-action__amount {
  font-size: 0.9rem;
  font-variant-numeric: tabular-nums;
}

.next-action__cta {
  margin-top: var(--space-1);
}
</style>
