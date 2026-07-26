<script setup lang="ts">
import type { PlanningHorizon } from '~/types/planning'
import { planningHorizonLabel } from '~/composables/use-planning'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { settings, loading, error, saving, load, save } = usePlanningSettings()
const { canWrite } = useOrganizationPermissions()

const defaultHorizon = ref<PlanningHorizon>('30_days')
const strategy = ref('none')
const reserveAmount = ref('')
const includeExpectedIncome = ref(true)
const includeEstimatedExpenses = ref(true)
const saveError = ref<string | null>(null)
const saved = ref(false)

onMounted(async () => {
  await load()
  if (settings.value) {
    defaultHorizon.value = settings.value.defaultHorizon
    strategy.value = settings.value.safetyReserveStrategy
    reserveAmount.value = settings.value.safetyReserveAmount || ''
    includeExpectedIncome.value = settings.value.includeExpectedIncome
    includeEstimatedExpenses.value = settings.value.includeEstimatedExpenses
  }
})

async function onSave() {
  saveError.value = null
  saved.value = false
  try {
    await save({
      version: settings.value?.version ?? null,
      defaultHorizon: defaultHorizon.value,
      safetyReserveStrategy: strategy.value,
      safetyReserveAmount: strategy.value === 'fixed_amount' ? reserveAmount.value : null,
      linkedEmergencyGoalId: null,
      includeExpectedIncome: includeExpectedIncome.value,
      includeEstimatedExpenses: includeEstimatedExpenses.value,
    })
    saved.value = true
  }
  catch (err) {
    saveError.value = err instanceof Error ? err.message : 'No se pudo guardar.'
  }
}

const horizons: PlanningHorizon[] = ['today', '7_days', '30_days', '90_days']
</script>

<template>
  <div class="settings-page stack">
    <header>
      <NuxtLink to="/app/planning">
        ← Planeación
      </NuxtLink>
      <h1>Configuración de planeación</h1>
      <p class="text-muted">
        Reserva de seguridad, horizonte y certeza de ingresos/gastos.
      </p>
    </header>

    <p v-if="error" class="error">
      {{ error }}
    </p>
    <div v-if="loading">
      <UiSkeleton height="8rem" />
    </div>
    <form
      v-else
      class="settings-form stack"
      @submit.prevent="onSave"
    >
      <label>
        <span>Horizonte por defecto</span>
        <select v-model="defaultHorizon" :disabled="!canWrite">
          <option
            v-for="item in horizons"
            :key="item"
            :value="item"
          >
            {{ planningHorizonLabel(item) }}
          </option>
        </select>
      </label>

      <label>
        <span>Reserva de seguridad</span>
        <select v-model="strategy" :disabled="!canWrite">
          <option value="none">
            Ninguna
          </option>
          <option value="fixed_amount">
            Monto fijo
          </option>
        </select>
      </label>

      <label v-if="strategy === 'fixed_amount'">
        <span>Monto de reserva</span>
        <input
          v-model="reserveAmount"
          type="text"
          inputmode="decimal"
          :disabled="!canWrite"
          required
        >
      </label>

      <label class="checkbox">
        <input v-model="includeExpectedIncome" type="checkbox" :disabled="!canWrite">
        Incluir ingresos esperados
      </label>
      <label class="checkbox">
        <input v-model="includeEstimatedExpenses" type="checkbox" :disabled="!canWrite">
        Incluir gastos estimados
      </label>

      <p v-if="saveError" class="error">
        {{ saveError }}
      </p>
      <p v-if="saved" class="ok">
        Guardado.
      </p>

      <UiButton
        v-if="canWrite"
        type="submit"
        variant="primary"
        :disabled="saving"
      >
        {{ saving ? 'Guardando…' : 'Guardar' }}
      </UiButton>
    </form>
  </div>
</template>

<style scoped>
.settings-page header h1 {
  margin: 0.5rem 0 0.25rem;
}
.settings-form label {
  display: grid;
  gap: 0.3rem;
}
.settings-form select,
.settings-form input[type='text'] {
  padding: 0.5rem 0.6rem;
  border-radius: 0.4rem;
  border: 1px solid var(--color-border, #d8dde6);
  max-width: 20rem;
}
.checkbox {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
}
.error {
  color: var(--color-danger, #b42318);
}
.ok {
  color: var(--color-success, #0f7a4c);
}
</style>
