<script setup lang="ts">
import type { CreatePlannedCashFlowInput, ScenarioAdjustmentInput } from '~/types/planning'
import { planningHorizonLabel } from '~/composables/use-planning'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const {
  horizon,
  currency,
  projection,
  simulation,
  activeProjection,
  loading,
  error,
  refresh,
  simulate,
  clearSimulation,
} = usePlanningProjection()

const cashFlows = usePlannedCashFlows()
const { canWrite } = useOrganizationPermissions()

const showManualForm = ref(false)
const manualName = ref('')
const manualAmount = ref('')
const manualDirection = ref<'inflow' | 'outflow'>('outflow')
const manualDate = ref('')
const manualError = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([refresh(), cashFlows.load(currency.value)])
})

watch(currency, () => {
  void cashFlows.load(currency.value)
})

async function onSimulate(adjustments: ScenarioAdjustmentInput[]) {
  await simulate(adjustments)
}

async function createManual() {
  manualError.value = null
  if (!manualName.value || !manualAmount.value || !manualDate.value) {
    manualError.value = 'Completa nombre, importe y fecha.'
    return
  }
  const payload: CreatePlannedCashFlowInput = {
    name: manualName.value.trim(),
    direction: manualDirection.value,
    amount: manualAmount.value,
    currency: currency.value,
    expectedAt: new Date(`${manualDate.value}T12:00:00`).toISOString(),
    certainty: 'expected',
  }
  try {
    await cashFlows.create(payload)
    showManualForm.value = false
    manualName.value = ''
    manualAmount.value = ''
    manualDate.value = ''
    await refresh()
  }
  catch (err) {
    manualError.value = err instanceof Error ? err.message : 'No se pudo crear el movimiento.'
  }
}
</script>

<template>
  <div class="planning-page stack">
    <header class="planning-page__header">
      <div>
        <h1>Planeación</h1>
        <p class="text-muted">
          ¿Cuánto puedes usar sin comprometer tu futuro?
        </p>
      </div>
      <div class="planning-page__actions">
        <PlanningHorizonSelector v-model="horizon" />
        <NuxtLink class="planning-page__settings" to="/app/planning/settings">
          Configuración
        </NuxtLink>
      </div>
    </header>

    <p v-if="error" class="planning-page__error">
      {{ error }}
    </p>

    <PlanningHeroCard
      :projection="activeProjection"
      :loading="loading && !activeProjection"
    />

    <p v-if="activeProjection" class="text-muted planning-page__horizon-note">
      {{ currency }} · próximos {{ planningHorizonLabel(horizon).toLowerCase() }}
    </p>

    <div v-if="loading && !activeProjection" class="stack">
      <UiSkeleton v-for="i in 4" :key="i" height="3rem" />
    </div>

    <template v-else-if="activeProjection">
      <UiEmptyState
        v-if="activeProjection.status === 'insufficient_data'"
        title="Planeación incompleta"
        description="Revisa tus cuentas líquidas y próximos movimientos para calcular Disponible para usar."
      />

      <PlanningSummaryCards
        v-else
        :projection="activeProjection"
      />

      <PlanningAlerts :alerts="activeProjection.alerts" />

      <div class="planning-page__grid">
        <PlanningUpcomingFlows :projection="activeProjection" />
        <PlanningBreakdown
          :items="activeProjection.breakdown"
          :currency="activeProjection.currency"
        />
      </div>

      <section v-if="canWrite" class="manual stack">
        <div class="manual__header">
          <h2>Movimientos planeados</h2>
          <UiButton
            type="button"
            size="sm"
            variant="secondary"
            @click="showManualForm = !showManualForm"
          >
            {{ showManualForm ? 'Cerrar' : '+ Agregar' }}
          </UiButton>
        </div>
        <form
          v-if="showManualForm"
          class="manual__form"
          @submit.prevent="createManual"
        >
          <input v-model="manualName" placeholder="Concepto" required>
          <select v-model="manualDirection">
            <option value="outflow">
              Gasto
            </option>
            <option value="inflow">
              Ingreso
            </option>
          </select>
          <input v-model="manualAmount" placeholder="Importe" inputmode="decimal" required>
          <input v-model="manualDate" type="date" required>
          <UiButton type="submit" size="sm" variant="primary">
            Guardar
          </UiButton>
        </form>
        <p v-if="manualError" class="planning-page__error">
          {{ manualError }}
        </p>
        <ul v-if="cashFlows.items.length" class="manual__list">
          <li v-for="item in cashFlows.items" :key="item.id">
            <span>{{ item.name }} · {{ item.direction }}</span>
            <UiButton
              type="button"
              size="sm"
              variant="ghost"
              @click="cashFlows.cancel(item.id).then(() => refresh())"
            >
              Cancelar
            </UiButton>
          </li>
        </ul>
      </section>

      <PlanningScenarioBuilder
        v-if="canWrite"
        @simulate="onSimulate"
        @clear="clearSimulation"
      />
      <PlanningScenarioComparison
        v-if="simulation"
        :simulation="simulation"
      />
    </template>
  </div>
</template>

<style scoped>
.planning-page__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  flex-wrap: wrap;
}
.planning-page__header h1 {
  margin: 0;
}
.planning-page__header p {
  margin: 0.25rem 0 0;
}
.planning-page__actions {
  display: flex;
  gap: 0.75rem;
  align-items: end;
}
.planning-page__settings {
  font-size: 0.9rem;
}
.planning-page__error {
  color: var(--color-danger, #b42318);
}
.planning-page__horizon-note {
  margin: 0;
}
.planning-page__grid {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
}
.manual__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.manual__header h2,
.manual h2 {
  margin: 0;
  font-size: 1.05rem;
}
.manual__form {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
}
.manual__form input,
.manual__form select {
  padding: 0.45rem 0.55rem;
  border-radius: 0.4rem;
  border: 1px solid var(--color-border, #d8dde6);
}
.manual__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.4rem;
}
.manual__list li {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}
@media (max-width: 640px) {
  .planning-page__header {
    flex-direction: column;
  }
}
</style>
