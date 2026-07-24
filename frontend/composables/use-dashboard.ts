import { createDashboardRepository } from '~/repositories/dashboard.repository'
import type {
  DashboardAttentionItem,
  DashboardMetric,
  DashboardModuleSummary,
  DashboardProjection,
  DashboardViewModel,
} from '~/types/dashboard'

function greetingForNow(displayName: string | undefined): string {
  const hour = new Date().getHours()
  const name = displayName?.trim() || 'hola'
  if (hour < 12) return `Buenos días, ${name}`
  if (hour < 19) return `Buenas tardes, ${name}`
  return `Buenas noches, ${name}`
}

function sliceForCurrency(projection: DashboardProjection, currency: string) {
  return projection.currencies.find(item => item.currency === currency)
    ?? projection.currencies[0]
}

function buildMetrics(
  projection: DashboardProjection,
  currency: string,
): DashboardMetric[] {
  const slice = sliceForCurrency(projection, currency)
  const sts = projection.safeToSpend

  return [
    {
      id: 'net_worth',
      label: 'Patrimonio neto',
      amount: slice?.netWorth ?? '0.00',
      currency,
      hint: 'Activos menos pasivos',
      trendAmount: slice?.monthlyNetFlow ?? null,
      trendLabel: 'flujo del mes',
      status: 'ready',
    },
    {
      id: 'liquid',
      label: 'Efectivo disponible',
      amount: slice?.liquidBalance ?? '0.00',
      currency,
      hint: 'Cuentas líquidas (checking, ahorro, efectivo, wallet)',
      status: 'ready',
    },
    {
      id: 'safe_to_spend',
      label: 'Disponible para gastar',
      amount: sts.status === 'available' ? sts.amount : null,
      currency: sts.currency ?? currency,
      hint: sts.status === 'available'
        ? 'Después de próximos pagos, impuestos y reserva mínima'
        : undefined,
      status: sts.status === 'available'
        ? 'ready'
        : sts.status === 'error'
          ? 'error'
          : 'not_configured',
      ctaLabel: sts.ctaLabel,
      ctaTo: sts.ctaTo,
    },
    {
      id: 'monthly_flow',
      label: 'Flujo del mes',
      amount: slice?.monthlyNetFlow ?? '0.00',
      currency,
      status: 'ready',
      detailLines: [
        { label: 'Ingresos', amount: slice?.monthlyIncome ?? '0.00' },
        { label: 'Gastos', amount: `-${slice?.monthlyExpenses ?? '0.00'}` },
        { label: 'Balance', amount: slice?.monthlyNetFlow ?? '0.00' },
      ],
    },
  ]
}

function moduleFromProjection(
  module: DashboardModuleSummary | null,
): DashboardModuleSummary | null {
  if (!module) return null
  if (module.status === 'available') {
    return { ...module, status: 'ready' }
  }
  return module
}

function toViewModel(
  projection: DashboardProjection,
  currency: string,
  displayName: string | undefined,
): DashboardViewModel {
  return {
    greeting: greetingForNow(displayName),
    subtitle: 'Así van tus finanzas hoy.',
    currency,
    availableCurrencies: projection.availableCurrencies,
    asOf: projection.asOf,
    metrics: buildMetrics(projection, currency),
    attentionItems: projection.attentionItems as DashboardAttentionItem[],
    onboarding: projection.onboarding,
    recentTransactions: projection.recentTransactions,
    cashFlow: projection.cashFlow.status === 'ready' ? projection.cashFlow : projection.cashFlow,
    budget: moduleFromProjection(projection.budget),
    primaryGoal: moduleFromProjection(projection.primaryGoal),
    debtSummary: moduleFromProjection(projection.debtSummary),
    taxSummary: moduleFromProjection(projection.taxSummary),
    upcoming: projection.upcoming,
    widgetErrors: projection.widgetErrors,
  }
}

export function useDashboard() {
  const auth = useAuthStore()
  const organization = useOrganizationStore()
  const preferences = usePreferencesStore()
  const cache = useFinanceCache()
  const { $api } = useNuxtApp()

  const loading = ref(true)
  const error = ref<string | null>(null)
  const projection = ref<DashboardProjection | null>(null)
  const view = ref<DashboardViewModel | null>(null)
  const selectedCurrency = ref<string>(
    preferences.preferredDashboardCurrency
      || organization.currentOrganization?.currency
      || 'MXN',
  )

  function clearView() {
    projection.value = null
    view.value = null
  }

  function applyCurrency(currency: string) {
    selectedCurrency.value = currency
    preferences.preferredDashboardCurrency = currency
    void load({ currency })
  }

  async function load(options: { currency?: string } = {}) {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización para ver tu panorama.'
      loading.value = false
      clearView()
      return
    }

    loading.value = true
    error.value = null
    clearView()

    const preferred = options.currency
      || preferences.preferredDashboardCurrency
      || organization.currentOrganization?.currency
      || undefined

    const repo = createDashboardRepository($api)

    try {
      const data = await repo.get(orgId, {
        period: 'this_month',
        currency: preferred,
      })
      projection.value = data

      const currency = preferred && data.availableCurrencies.includes(preferred)
        ? preferred
        : data.selectedCurrency

      selectedCurrency.value = currency
      if (preferences.preferredDashboardCurrency !== currency) {
        preferences.preferredDashboardCurrency = currency
      }
      view.value = toViewModel(data, currency, auth.user?.displayName)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo cargar el dashboard.'
      clearView()
    } finally {
      loading.value = false
    }
  }

  watch(
    () => organization.currentOrganizationId,
    () => {
      clearView()
      void load()
    },
  )

  watch(
    () => cache.dashboardVersion.value,
    () => {
      void load({ currency: selectedCurrency.value })
    },
  )

  return {
    loading,
    error,
    view,
    projection,
    selectedCurrency,
    applyCurrency,
    load,
    clearView,
  }
}
