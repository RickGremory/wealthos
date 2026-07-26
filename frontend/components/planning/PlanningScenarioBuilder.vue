<script setup lang="ts">
import type { CashFlowDirection, ScenarioAdjustmentInput } from '~/types/planning'

const emit = defineEmits<{
  simulate: [adjustments: ScenarioAdjustmentInput[]]
  clear: []
}>()

const direction = ref<CashFlowDirection>('outflow')
const amount = ref('')
const label = ref('')
const expectedAt = ref('')

function submit() {
  if (!amount.value || !label.value || !expectedAt.value) return
  const when = new Date(`${expectedAt.value}T12:00:00`)
  emit('simulate', [
    {
      kind: 'add_cash_flow',
      direction: direction.value,
      amount: amount.value,
      expectedAt: when.toISOString(),
      label: label.value.trim(),
      certainty: 'expected',
    },
  ])
}
</script>

<template>
  <section class="scenario">
    <h2>¿Qué pasa si…?</h2>
    <p class="text-muted">
      Simula un ingreso o gasto sin cambiar tus datos reales.
    </p>
    <form class="scenario__form" @submit.prevent="submit">
      <label>
        <span>Tipo</span>
        <select v-model="direction">
          <option value="outflow">
            Gasto
          </option>
          <option value="inflow">
            Ingreso
          </option>
        </select>
      </label>
      <label>
        <span>Concepto</span>
        <input v-model="label" type="text" maxlength="120" required>
      </label>
      <label>
        <span>Importe</span>
        <input v-model="amount" type="text" inputmode="decimal" required placeholder="20000.00">
      </label>
      <label>
        <span>Fecha</span>
        <input v-model="expectedAt" type="date" required>
      </label>
      <div class="scenario__actions">
        <UiButton type="submit" variant="primary" size="sm">
          Simular
        </UiButton>
        <UiButton type="button" variant="ghost" size="sm" @click="emit('clear')">
          Descartar
        </UiButton>
      </div>
    </form>
  </section>
</template>

<style scoped>
.scenario h2 {
  margin: 0 0 0.35rem;
  font-size: 1.05rem;
}
.scenario__form {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.65rem;
  grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
}
.scenario__form label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.85rem;
}
.scenario__form input,
.scenario__form select {
  padding: 0.45rem 0.55rem;
  border-radius: 0.4rem;
  border: 1px solid var(--color-border, #d8dde6);
}
.scenario__actions {
  display: flex;
  gap: 0.5rem;
  align-items: end;
}
</style>
