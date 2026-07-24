<script setup lang="ts">
import type { GoalAccountOption, GoalStrategy } from '~/types/goals'
import { GOAL_STRATEGY_OPTIONS } from '~/utils/goal-strategies'

const strategy = defineModel<GoalStrategy>('strategy', { required: true })
const linkedAccountIds = defineModel<string[]>('linkedAccountIds', { default: () => [] })

const props = withDefaults(
  defineProps<{
    accounts?: GoalAccountOption[]
    accountsLoading?: boolean
    disabled?: boolean
    locked?: boolean
    error?: string
  }>(),
  {
    accounts: () => [],
    accountsLoading: false,
    disabled: false,
    locked: false,
    error: undefined,
  },
)

function toggleAccount(id: string) {
  if (props.disabled || props.locked) return
  const set = new Set(linkedAccountIds.value)
  if (set.has(id)) set.delete(id)
  else set.add(id)
  linkedAccountIds.value = [...set]
}

function isChecked(id: string) {
  return linkedAccountIds.value.includes(id)
}
</script>

<template>
  <fieldset class="strategy-selector" data-testid="goal-strategy-selector" :disabled="disabled || locked">
    <legend class="strategy-selector__legend">Cómo medir el progreso</legend>
    <p v-if="locked" class="text-muted strategy-selector__lock-hint">
      La estrategia no se puede cambiar después de crear la meta.
    </p>

    <div class="strategy-selector__options">
      <label
        v-for="option in GOAL_STRATEGY_OPTIONS"
        :key="option.value"
        class="strategy-selector__option"
        :data-active="strategy === option.value"
      >
        <input
          v-model="strategy"
          type="radio"
          name="goal-strategy"
          :value="option.value"
          :disabled="disabled || locked"
        >
        <span class="strategy-selector__option-body">
          <strong>{{ option.label }}</strong>
          <span class="text-muted">{{ option.description }}</span>
        </span>
      </label>
    </div>

    <div
      v-if="strategy === 'linked_accounts'"
      class="strategy-selector__accounts"
      data-testid="goal-linked-accounts"
    >
      <p class="strategy-selector__accounts-title">Cuentas vinculadas</p>
      <p v-if="accountsLoading" class="text-muted">Cargando cuentas…</p>
      <p v-else-if="!accounts.length" class="text-muted">
        No hay cuentas de activo en esta moneda. Crea una cuenta o cambia la moneda.
      </p>
      <div v-else class="strategy-selector__account-list">
        <label
          v-for="account in accounts"
          :key="account.id"
          class="strategy-selector__account"
        >
          <input
            type="checkbox"
            :checked="isChecked(account.id)"
            :disabled="disabled"
            @change="toggleAccount(account.id)"
          >
          <span>
            <strong>{{ account.name }}</strong>
            <span class="text-muted">
              ·
              <MoneyValue
                :amount="account.currentBalance"
                :currency="account.currency"
                :emphasize-sign="false"
              />
            </span>
          </span>
        </label>
      </div>
      <p v-if="error" class="strategy-selector__error">{{ error }}</p>
    </div>
  </fieldset>
</template>

<style scoped>
.strategy-selector {
  border: 0;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.strategy-selector__legend {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
  padding: 0;
}

.strategy-selector__lock-hint {
  margin: 0;
  font-size: 0.85rem;
}

.strategy-selector__options {
  display: grid;
  gap: var(--space-2);
}

.strategy-selector__option {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  cursor: pointer;
  background: var(--color-surface);
}

.strategy-selector__option[data-active='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}

.strategy-selector__option input {
  margin-top: 0.2rem;
}

.strategy-selector__option-body {
  display: grid;
  gap: 0.2rem;
  font-size: 0.88rem;
}

.strategy-selector__accounts {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-slate-50, #f8fafc);
}

.strategy-selector__accounts-title {
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.strategy-selector__account-list {
  display: grid;
  gap: var(--space-2);
}

.strategy-selector__account {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  font-size: 0.9rem;
  cursor: pointer;
}

.strategy-selector__error {
  margin: 0;
  color: var(--color-danger);
  font-size: 0.8rem;
}
</style>
