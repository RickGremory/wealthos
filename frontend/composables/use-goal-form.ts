import { createAccountsRepository } from '~/repositories/accounts.repository'
import { createGoalsRepository } from '~/repositories/goals.repository'
import type {
  CreateGoalFormModel,
  GoalAccountOption,
  GoalDetailView,
  GoalPriority,
  GoalStrategy,
  UpdateGoalFormModel,
} from '~/types/goals'
import { getGoalTemplate } from '~/utils/goal-templates'
import { toUserMessage } from '~/lib/api/errors'
import { compareDecimalStrings } from '~/utils/decimal-string'
import { todayLocalIsoDate } from '~/composables/use-date'

const CURRENCY_OPTIONS = [
  { label: 'MXN — Peso mexicano', value: 'MXN' },
  { label: 'USD — Dólar estadounidense', value: 'USD' },
  { label: 'EUR — Euro', value: 'EUR' },
]

function normalizeAmount(raw: string): string {
  const trimmed = raw.trim().replace(/,/g, '')
  if (!trimmed) return ''
  const [whole = '0', frac = ''] = trimmed.split('.')
  return `${whole}.${(frac + '00').slice(0, 2)}`
}

export function useGoalForm(mode: 'create' | 'edit' = 'create') {
  const organization = useOrganizationStore()
  const preferences = usePreferencesStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()
  const toast = useToast()

  const form = reactive<CreateGoalFormModel>({
    name: '',
    targetAmount: '',
    currency: organization.currentOrganization?.currency || 'MXN',
    strategy: 'manual',
    targetDate: '',
    linkedAccountIds: [],
    priority: 2,
    templateId: null,
  })

  const editForm = reactive<UpdateGoalFormModel>({
    name: '',
    targetAmount: '',
    targetDate: '',
    linkedAccountIds: [],
    priority: 2,
  })

  /** Locked fields when editing (strategy/currency cannot change). */
  const editMeta = reactive<{
    strategy: GoalStrategy
    currency: string
    status: string
  }>({
    strategy: 'manual',
    currency: 'MXN',
    status: 'active',
  })

  const accounts = ref<GoalAccountOption[]>([])
  const accountsLoading = ref(false)
  const submitting = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<Record<string, string>>({})

  const currencyOptions = CURRENCY_OPTIONS

  const linkableAccounts = computed(() => {
    const currency = mode === 'create' ? form.currency : editMeta.currency
    return accounts.value.filter(
      a => a.currency === currency && a.accountType !== 'credit_card' && a.accountType !== 'loan',
    )
  })

  function clearFieldErrors() {
    fieldErrors.value = {}
  }

  function resetCreate(defaults?: Partial<CreateGoalFormModel>) {
    form.name = defaults?.name ?? ''
    form.targetAmount = defaults?.targetAmount ?? ''
    form.currency = defaults?.currency
      ?? organization.currentOrganization?.currency
      ?? 'MXN'
    form.strategy = defaults?.strategy ?? 'manual'
    form.targetDate = defaults?.targetDate ?? ''
    form.linkedAccountIds = defaults?.linkedAccountIds ?? []
    form.priority = defaults?.priority ?? 2
    form.templateId = defaults?.templateId ?? null
    error.value = null
    clearFieldErrors()
  }

  function applyTemplate(templateId: string) {
    const template = getGoalTemplate(templateId)
    if (!template) return
    form.templateId = template.id
    form.name = template.name
    form.targetAmount = template.suggestedTargetAmount
    form.strategy = template.strategyHint
    if (form.strategy !== 'linked_accounts') {
      form.linkedAccountIds = []
    }
  }

  function loadEdit(goal: GoalDetailView) {
    editForm.name = goal.name
    editForm.targetAmount = goal.targetAmount
    editForm.targetDate = goal.targetDate ?? ''
    editForm.linkedAccountIds = [...goal.linkedAccountIds]
    editForm.priority = preferences.getGoalPriority(goal.id)
    editMeta.strategy = goal.strategy
    editMeta.currency = goal.currency
    editMeta.status = goal.status
    error.value = null
    clearFieldErrors()
  }

  function validateCreate(): boolean {
    clearFieldErrors()
    const next: Record<string, string> = {}

    if (!form.name.trim() || form.name.trim().length < 2) {
      next.name = 'El nombre debe tener al menos 2 caracteres.'
    }

    const amount = normalizeAmount(form.targetAmount)
    if (!amount || !/^\d+(\.\d{1,2})?$/.test(amount) || compareDecimalStrings(amount, '0') <= 0) {
      next.targetAmount = 'Ingresa un monto objetivo mayor a cero.'
    }

    if (!form.currency || form.currency.length !== 3) {
      next.currency = 'Selecciona una moneda.'
    }

    if (form.targetDate) {
      if (form.targetDate < todayLocalIsoDate()) {
        next.targetDate = 'La fecha objetivo debe ser hoy o en el futuro.'
      }
    }

    if (form.strategy === 'linked_accounts' && form.linkedAccountIds.length === 0) {
      next.linkedAccountIds = 'Selecciona al menos una cuenta vinculada.'
    }

    fieldErrors.value = next
    return Object.keys(next).length === 0
  }

  function validateEdit(): boolean {
    clearFieldErrors()
    const next: Record<string, string> = {}

    if (!editForm.name.trim() || editForm.name.trim().length < 2) {
      next.name = 'El nombre debe tener al menos 2 caracteres.'
    }

    const amount = normalizeAmount(editForm.targetAmount)
    if (!amount || !/^\d+(\.\d{1,2})?$/.test(amount) || compareDecimalStrings(amount, '0') <= 0) {
      next.targetAmount = 'Ingresa un monto objetivo mayor a cero.'
    }

    if (editForm.targetDate && editForm.targetDate < todayLocalIsoDate()) {
      next.targetDate = 'La fecha objetivo debe ser hoy o en el futuro.'
    }

    if (
      editMeta.strategy === 'linked_accounts'
      && editForm.linkedAccountIds.length === 0
    ) {
      next.linkedAccountIds = 'Selecciona al menos una cuenta vinculada.'
    }

    fieldErrors.value = next
    return Object.keys(next).length === 0
  }

  async function loadAccounts() {
    const orgId = organization.currentOrganizationId
    if (!orgId) return

    accountsLoading.value = true
    try {
      const repo = createAccountsRepository($api)
      const raw = await repo.list(orgId)
      accounts.value = raw
        .filter(a => a.isActive && a.classification === 'asset')
        .map(a => ({
          id: a.id,
          name: a.name,
          currency: a.currency,
          currentBalance: a.currentBalance,
          accountType: a.accountType,
        }))
    }
    catch {
      accounts.value = []
    }
    finally {
      accountsLoading.value = false
    }
  }

  async function submitCreate(): Promise<string | null> {
    error.value = null
    if (!validateCreate()) return null

    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      return null
    }

    submitting.value = true
    try {
      const repo = createGoalsRepository($api)
      const goal = await repo.create(orgId, {
        name: form.name.trim(),
        targetAmount: normalizeAmount(form.targetAmount),
        currency: form.currency,
        strategy: form.strategy,
        targetDate: form.targetDate || null,
        linkedAccountIds:
          form.strategy === 'linked_accounts' ? form.linkedAccountIds : [],
      })
      preferences.setGoalPriority(goal.id, form.priority as GoalPriority)
      if (form.priority === 1 && !preferences.preferredPrimaryGoalId) {
        preferences.preferredPrimaryGoalId = goal.id
      }
      cache.invalidateGoals()
      toast.success('Meta creada', goal.name)
      return goal.id
    }
    catch (e) {
      error.value = toUserMessage(e)
      return null
    }
    finally {
      submitting.value = false
    }
  }

  async function submitEdit(goalId: string): Promise<boolean> {
    error.value = null
    if (!validateEdit()) return false

    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      return false
    }

    submitting.value = true
    try {
      const repo = createGoalsRepository($api)
      const payload: {
        name: string
        targetAmount: string
        targetDate: string | null
        linkedAccountIds?: string[]
      } = {
        name: editForm.name.trim(),
        targetAmount: normalizeAmount(editForm.targetAmount),
        targetDate: editForm.targetDate || null,
      }
      if (editMeta.strategy === 'linked_accounts') {
        payload.linkedAccountIds = editForm.linkedAccountIds
      }

      await repo.update(orgId, goalId, payload)
      preferences.setGoalPriority(goalId, editForm.priority as GoalPriority)
      cache.invalidateGoals()
      toast.success('Meta actualizada')
      return true
    }
    catch (e) {
      error.value = toUserMessage(e)
      return false
    }
    finally {
      submitting.value = false
    }
  }

  return {
    mode,
    form,
    editForm,
    editMeta,
    accounts,
    linkableAccounts,
    accountsLoading,
    submitting,
    error,
    fieldErrors,
    currencyOptions,
    resetCreate,
    applyTemplate,
    loadEdit,
    loadAccounts,
    validateCreate,
    validateEdit,
    submitCreate,
    submitEdit,
  }
}
