import {
  createDashboardRepository,
  enhanceGoalModuleSummary,
} from '~/repositories/dashboard.repository'
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
  multiCurrency: boolean,
): DashboardMetric[] {
  const slice = sliceForCurrency(projection, currency)
  const sts = projection.safeToSpend
  const hasSlice = projection.currencies.some(item => item.currency === currency)
  const emptyHint = multiCurrency
    ? `Sin movimientos en ${currency}. Los importes no se mezclan con otras monedas.`
    : undefined
  const currencyHint = multiCurrency
    ? `Calculado solo con cuentas ${currency}. WealthOS no convierte entre monedas.`
    : 'Activos menos pasivos'

  return [
    {
      id: 'net_worth',
      label: `Patrimonio neto (${currency})`,
      amount: hasSlice ? (slice?.netWorth ?? '0.00') : null,
      currency,
      hint: hasSlice ? currencyHint : emptyHint,
      trendAmount: hasSlice ? (slice?.monthlyNetFlow ?? null) : null,
      trendLabel: 'flujo del mes',
      status: hasSlice ? 'ready' : 'empty',
    },
    {
      id: 'liquid',
      label: `Efectivo disponible (${currency})`,
      amount: hasSlice ? (slice?.liquidBalance ?? '0.00') : null,
      currency,
      hint: hasSlice
        ? 'Cuentas líquidas (checking, ahorro, efectivo, wallet)'
        : emptyHint,
      status: hasSlice ? 'ready' : 'empty',
    },
    {
      id: 'safe_to_spend',
      label: `Disponible para usar (${currency})`,
      amount: sts.status === 'available' && (sts.currency === currency || !sts.currency)
        ? sts.amount
        : null,
      currency: sts.currency ?? currency,
      hint: sts.status === 'available'
        ? 'Después de próximos pagos, impuestos y reserva mínima'
        : undefined,
      status: sts.status === 'available' && (sts.currency === currency || !sts.currency)
        ? 'ready'
        : sts.status === 'error'
          ? 'error'
          : 'not_configured',
      ctaLabel: sts.ctaLabel,
      ctaTo: sts.ctaTo,
    },
    {
      id: 'monthly_flow',
      label: `Flujo del mes (${currency})`,
      amount: hasSlice ? (slice?.monthlyNetFlow ?? '0.00') : null,
      currency,
      status: hasSlice ? 'ready' : 'empty',
      detailLines: hasSlice
        ? [
            { label: 'Ingresos', amount: slice?.monthlyIncome ?? '0.00' },
            { label: 'Gastos', amount: `-${slice?.monthlyExpenses ?? '0.00'}` },
            { label: 'Balance', amount: slice?.monthlyNetFlow ?? '0.00' },
          ]
        : undefined,
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
  const multiCurrency = projection.availableCurrencies.length > 1
  return {
    greeting: greetingForNow(displayName),
    subtitle: multiCurrency
      ? `Perspectiva en ${currency}. Los importes no se mezclan entre monedas.`
      : 'Así van tus finanzas hoy.',
    currency,
    availableCurrencies: projection.availableCurrencies,
    asOf: projection.asOf,
    metrics: buildMetrics(projection, currency, multiCurrency),
    attentionItems: projection.attentionItems as DashboardAttentionItem[],
    onboarding: projection.onboarding,
    recentTransactions: projection.recentTransactions.filter(tx => tx.currency === currency),
    cashFlow: projection.cashFlow.status === 'ready' ? projection.cashFlow : projection.cashFlow,
    budget: moduleFromProjection(projection.budget),
    primaryGoal: enhanceGoalModuleSummary(moduleFromProjection(projection.primaryGoal)),
    debtSummary: moduleFromProjection(projection.debtSummary),
    taxSummary: moduleFromProjection(projection.taxSummary),
    upcoming: projection.upcoming.filter(item => !item.currency || item.currency === currency),
    financialCommitments: projection.financialCommitments,
    widgetErrors: projection.widgetErrors,
    multiCurrency,
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
