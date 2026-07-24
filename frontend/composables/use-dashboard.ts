import { createDashboardRepository } from '~/repositories/dashboard.repository'
import type {
  DashboardAttentionItem,
  DashboardMetric,
  DashboardModuleSummary,
  DashboardOnboarding,
  DashboardViewModel,
} from '~/types/dashboard'

function greetingForNow(displayName: string | undefined): string {
  const hour = new Date().getHours()
  const name = displayName?.trim() || 'hola'
  if (hour < 12) return `Buenos días, ${name}`
  if (hour < 19) return `Buenas tardes, ${name}`
  return `Buenas noches, ${name}`
}

function buildOnboarding(input: {
  hasAccounts: boolean
  hasTransactions: boolean
  hasIncome: boolean
  hasExpense: boolean
  hasBudget: boolean
}): DashboardOnboarding {
  const steps = [
    {
      id: 'account',
      label: 'Crea tu primera cuenta',
      description: 'Checking, ahorro o efectivo para empezar.',
      completed: input.hasAccounts,
      to: '/app/accounts',
    },
    {
      id: 'balance',
      label: 'Registra tu saldo inicial',
      description: 'Así calculamos tu patrimonio real.',
      completed: input.hasAccounts,
      to: '/app/accounts',
    },
    {
      id: 'income',
      label: 'Registra un ingreso',
      description: 'Un cobro reciente basta para activar el flujo.',
      completed: input.hasIncome,
      to: '/app/transactions',
    },
    {
      id: 'expense',
      label: 'Registra un gasto',
      description: 'Empieza a ver en qué se va el dinero.',
      completed: input.hasExpense,
      to: '/app/transactions',
    },
    {
      id: 'budget',
      label: 'Crea un presupuesto',
      description: 'Define cuánto puedes gastar este mes.',
      completed: input.hasBudget,
      to: '/app/planning',
    },
  ]

  const completedSteps = steps.filter(step => step.completed).length
  return {
    completed: completedSteps === steps.length,
    completedSteps,
    totalSteps: steps.length,
    steps,
  }
}

function emptyModule(
  title: string,
  hint: string,
  ctaLabel: string,
  ctaTo: string,
): DashboardModuleSummary {
  return {
    status: 'not_configured',
    title,
    lines: [],
    hint,
    ctaLabel,
    ctaTo,
  }
}

export function useDashboard() {
  const auth = useAuthStore()
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()

  const loading = ref(true)
  const error = ref<string | null>(null)
  const view = ref<DashboardViewModel | null>(null)

  async function load() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización para ver tu panorama.'
      loading.value = false
      return
    }

    loading.value = true
    error.value = null

    const repo = createDashboardRepository($api)

    try {
      const [summary, recent, planning] = await Promise.all([
        repo.getSummary(orgId),
        repo.getRecentTransactions(orgId, 8),
        repo.getSafeToSpend(orgId),
      ])

      const currency = summary.currency
        || organization.currentOrganization?.currency
        || 'MXN'

      const hasIncome = recent.some(item => item.transactionType === 'income')
      const hasExpense = recent.some(item => item.transactionType === 'expense')
      const onboarding = buildOnboarding({
        hasAccounts: summary.activeAccounts > 0,
        hasTransactions: summary.transactionCount > 0 || recent.length > 0,
        hasIncome: hasIncome || Number(summary.monthlyIncome) > 0,
        hasExpense: hasExpense || Number(summary.monthlyExpenses) > 0,
        hasBudget: Boolean(planning?.configured),
      })

      const metrics: DashboardMetric[] = [
        {
          id: 'net_worth',
          label: 'Patrimonio neto',
          amount: summary.netWorth,
          currency,
          hint: 'Activos menos pasivos',
          trendAmount: summary.monthlyNetFlow,
          trendLabel: 'flujo del mes',
          status: 'ready',
        },
        {
          id: 'liquid',
          label: 'Efectivo disponible',
          amount: summary.totalAssets,
          currency,
          hint: 'Activos líquidos reportados',
          status: 'ready',
        },
        {
          id: 'safe_to_spend',
          label: 'Disponible para gastar',
          amount: planning?.safeToSpend ?? null,
          currency: planning?.currency ?? currency,
          hint: planning?.configured
            ? 'Después de próximos pagos, impuestos y reserva mínima'
            : undefined,
          status: planning?.configured && planning.safeToSpend != null
            ? 'ready'
            : 'not_configured',
          ctaLabel: 'Configura tu flujo de caja',
          ctaTo: '/app/planning',
        },
        {
          id: 'monthly_flow',
          label: 'Flujo del mes',
          amount: summary.monthlyNetFlow,
          currency,
          status: 'ready',
          detailLines: [
            { label: 'Ingresos', amount: summary.monthlyIncome },
            { label: 'Gastos', amount: `-${summary.monthlyExpenses}` },
            { label: 'Balance', amount: summary.monthlyNetFlow },
          ],
        },
      ]

      const attentionItems: DashboardAttentionItem[] = []
      if (!onboarding.completed) {
        attentionItems.push({
          id: 'onboarding',
          severity: 'info',
          title: 'Completa tu panorama inicial',
          message: `Llevas ${onboarding.completedSteps} de ${onboarding.totalSteps} pasos. Cada uno revela más de tu salud financiera.`,
          actionLabel: 'Ver checklist',
          actionTo: '#onboarding',
        })
      }
      if (summary.taxBalance && Number(summary.taxBalance) > 0) {
        attentionItems.push({
          id: 'tax_balance',
          severity: 'warning',
          title: 'Impuestos por cubrir',
          message: 'Hay un saldo fiscal estimado pendiente este periodo.',
          amount: summary.taxBalance,
          currency,
          actionLabel: 'Revisar impuestos',
          actionTo: '/app/taxes',
        })
      }
      if (summary.activeDebts > 0 && summary.debtMinimumPayments) {
        attentionItems.push({
          id: 'debt_payment',
          severity: 'info',
          title: 'Pagos mínimos activos',
          message: `Tienes ${summary.activeDebts} deuda(s) con pagos mínimos programables.`,
          amount: summary.debtMinimumPayments,
          currency,
          actionLabel: 'Ver deudas',
          actionTo: '/app/debts',
        })
      }

      const budget: DashboardModuleSummary | null = planning?.configured
        ? {
            status: 'ready',
            title: 'Presupuesto del mes',
            lines: [
              { label: 'Estado', value: 'Planificación activa' },
            ],
            hint: 'Abre Planning para ver el ritmo de gasto.',
            ctaLabel: 'Ver presupuesto',
            ctaTo: '/app/planning',
          }
        : emptyModule(
            'Presupuesto del mes',
            'Crea un presupuesto para controlar tu ritmo de gasto.',
            'Crear presupuesto',
            '/app/planning',
          )

      const primaryGoal: DashboardModuleSummary | null = summary.goalsActive > 0
        ? {
            status: 'ready',
            title: 'Metas',
            lines: [
              { label: 'Activas', value: String(summary.goalsActive) },
              { label: 'Completadas', value: String(summary.goalsCompleted) },
            ],
            ctaLabel: 'Ver metas',
            ctaTo: '/app/goals',
          }
        : emptyModule(
            'Metas',
            'Define una meta prioritaria para dar dirección a tu ahorro.',
            'Crear meta',
            '/app/goals',
          )

      const debtSummary: DashboardModuleSummary | null = summary.activeDebts > 0
        ? {
            status: 'ready',
            title: 'Deudas',
            lines: [
              { label: 'Deuda total', value: summary.totalDebt ?? '0.00' },
              { label: 'Pagos mínimos', value: summary.debtMinimumPayments ?? '0.00' },
            ],
            ctaLabel: 'Ver deudas',
            ctaTo: '/app/debts',
          }
        : emptyModule(
            'Deudas',
            'Registra tus pasivos para ver pagos próximos y progreso.',
            'Agregar deuda',
            '/app/debts',
          )

      const taxSummary: DashboardModuleSummary | null = summary.taxEstimated != null
        ? {
            status: 'ready',
            title: 'Impuestos estimados',
            lines: [
              { label: 'Por pagar', value: summary.taxBalance ?? '0.00' },
              { label: 'Pagado', value: summary.taxPaid ?? '0.00' },
              { label: 'Estimado', value: summary.taxEstimated },
            ],
            ctaLabel: 'Revisar cálculo',
            ctaTo: '/app/taxes',
          }
        : emptyModule(
            'Impuestos',
            'Configura tu perfil fiscal para estimar reservas.',
            'Configurar impuestos',
            '/app/taxes',
          )

      view.value = {
        greeting: greetingForNow(auth.user?.displayName),
        subtitle: 'Así están tus finanzas hoy.',
        currency,
        asOf: new Date().toISOString(),
        metrics,
        attentionItems: attentionItems.slice(0, 4),
        onboarding,
        recentTransactions: recent,
        budget,
        primaryGoal,
        debtSummary,
        taxSummary,
        upcoming: [],
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'No se pudo cargar el dashboard.'
      view.value = null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    view,
    load,
  }
}
