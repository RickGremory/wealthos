<script setup lang="ts">
import type { TransactionType } from '~/types/transactions'

const model = defineModel<TransactionType>({ default: 'expense' })

withDefaults(
  defineProps<{
    allowAdjustment?: boolean
    compact?: boolean
  }>(),
  {
    allowAdjustment: true,
    compact: false,
  },
)

const showMore = ref(false)

const primaryTypes: Array<{ value: TransactionType, label: string }> = [
  { value: 'expense', label: 'Gasto' },
  { value: 'income', label: 'Ingreso' },
  { value: 'transfer', label: 'Transferencia' },
]

function select(type: TransactionType) {
  model.value = type
  if (type === 'adjustment') showMore.value = false
}
</script>

<template>
  <div class="type-selector" data-testid="transaction-type-selector">
    <div class="type-selector__primary" :class="{ 'type-selector__primary--compact': compact }">
      <button
        v-for="item in primaryTypes"
        :key="item.value"
        type="button"
        class="type-selector__chip"
        :class="{ 'type-selector__chip--active': model === item.value }"
        @click="select(item.value)"
      >
        {{ item.label }}
      </button>
    </div>

    <div v-if="allowAdjustment" class="type-selector__more">
      <button
        type="button"
        class="type-selector__more-btn"
        @click="showMore = !showMore"
      >
        Más {{ showMore ? '▴' : '→' }}
      </button>
      <button
        v-if="showMore || model === 'adjustment'"
        type="button"
        class="type-selector__chip type-selector__chip--secondary"
        :class="{ 'type-selector__chip--active': model === 'adjustment' }"
        @click="select('adjustment')"
      >
        Ajustar saldo
      </button>
    </div>
  </div>
</template>

<style scoped>
.type-selector {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.type-selector__primary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-2);
}

.type-selector__primary--compact {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.type-selector__chip {
  border: 1px solid var(--color-border-strong);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 0.55rem 0.5rem;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-slate-700);
  cursor: pointer;
}

.type-selector__chip--active {
  background: var(--color-teal-50);
  border-color: var(--color-teal-700);
  color: var(--color-teal-900);
}

.type-selector__chip--secondary {
  width: 100%;
}

.type-selector__more {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.type-selector__more-btn {
  align-self: flex-start;
  border: 0;
  background: transparent;
  color: var(--color-teal-800);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0;
}
</style>
