import { createPlanningRepository } from '~/repositories/planning.repository'
import type {
  PlanningHorizon,
  PlanningProjection,
  ScenarioAdjustmentInput,
  ScenarioSimulation,
} from '~/types/planning'
import { toUserMessage } from '~/lib/api/errors'

const STATUS_LABELS: Record<string, string> = {
  healthy: 'Saludable',
  limited: 'Limitado',
  zero: 'En cero',
  deficit: 'Déficit de reserva',
  insufficient_data: 'Datos insuficientes',
  unavailable: 'No disponible',
}

const CONFIDENCE_LABELS: Record<string, string> = {
  high: 'Alta',
  medium: 'Media',
  low: 'Baja',
}

const HORIZON_LABELS: Record<PlanningHorizon, string> = {
  today: 'Hoy',
  '7_days': '7 días',
  '30_days': '30 días',
  '90_days': '90 días',
}

export function planningStatusLabel(status: string): string {
  return STATUS_LABELS[status] || status
}

export function planningConfidenceLabel(confidence: string): string {
  return CONFIDENCE_LABELS[confidence] || confidence
}

export function planningHorizonLabel(horizon: PlanningHorizon): string {
  return HORIZON_LABELS[horizon]
}

export function usePlanningProjection() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const repo = createPlanningRepository($api)

  const horizon = ref<PlanningHorizon>('30_days')
  const currency = computed(() => organization.currentOrganization?.currency || 'MXN')
  const projection = ref<PlanningProjection | null>(null)
  const simulation = ref<ScenarioSimulation | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function refresh() {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    loading.value = true
    error.value = null
    try {
      projection.value = await repo.getProjection(orgId, {
        currency: currency.value,
        horizon: horizon.value,
      })
      simulation.value = null
    }
    catch (err) {
      error.value = toUserMessage(err)
      projection.value = null
    }
    finally {
      loading.value = false
    }
  }

  async function simulate(adjustments: ScenarioAdjustmentInput[]) {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    loading.value = true
    error.value = null
    try {
      simulation.value = await repo.simulate(orgId, {
        currency: currency.value,
        horizon: horizon.value,
        adjustments,
      })
    }
    catch (err) {
      error.value = toUserMessage(err)
    }
    finally {
      loading.value = false
    }
  }

  function clearSimulation() {
    simulation.value = null
  }

  const activeProjection = computed(() => simulation.value?.scenario ?? projection.value)

  watch([horizon, currency], () => {
    void refresh()
  })

  return {
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
  }
}

export function usePlanningSettings() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const repo = createPlanningRepository($api)
  const settings = ref(null as Awaited<ReturnType<typeof repo.getSettings>> | null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const saving = ref(false)

  async function load() {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    loading.value = true
    error.value = null
    try {
      settings.value = await repo.getSettings(orgId)
    }
    catch (err) {
      error.value = toUserMessage(err)
    }
    finally {
      loading.value = false
    }
  }

  async function save(input: Parameters<typeof repo.updateSettings>[1]) {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    saving.value = true
    error.value = null
    try {
      settings.value = await repo.updateSettings(orgId, input)
    }
    catch (err) {
      error.value = toUserMessage(err)
      throw err
    }
    finally {
      saving.value = false
    }
  }

  return { settings, loading, error, saving, load, save }
}

export function usePlannedCashFlows() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const repo = createPlanningRepository($api)
  const items = ref([] as Awaited<ReturnType<typeof repo.listCashFlows>>)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function load(currency?: string) {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    loading.value = true
    error.value = null
    try {
      items.value = await repo.listCashFlows(orgId, {
        currency,
        status: 'active',
      })
    }
    catch (err) {
      error.value = toUserMessage(err)
    }
    finally {
      loading.value = false
    }
  }

  async function create(input: Parameters<typeof repo.createCashFlow>[1]) {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    const created = await repo.createCashFlow(orgId, input)
    items.value = [created, ...items.value]
    return created
  }

  async function cancel(cashFlowId: string) {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    await repo.cancelCashFlow(orgId, cashFlowId)
    items.value = items.value.filter(item => item.id !== cashFlowId)
  }

  return { items, loading, error, load, create, cancel }
}
