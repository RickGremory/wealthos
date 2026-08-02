import { createAccountsRepository } from '~/repositories/accounts.repository'
import { createCategoriesRepository } from '~/repositories/categories.repository'
import { createRecurringRepository } from '~/repositories/recurring.repository'
import type { AccountSummary } from '~/types/domain'
import type { CategoryTreeNodeView } from '~/types/categories'
import type {
  CreateRecurringRuleInput,
  RecurrencePatternInput,
  RecurringFormModel,
  RecurringPreviewView,
} from '~/types/recurring'
import { toUserMessage } from '~/lib/api/errors'
import { todayLocalIsoDate } from '~/composables/use-date'

function emptyForm(currency = 'MXN'): RecurringFormModel {
  const today = todayLocalIsoDate()
  return {
    name: '',
    direction: 'outflow',
    amount: '',
    currency,
    frequency: 'monthly',
    interval: 1,
    dayOfMonth: 15,
    endOfMonth: false,
    daysOfWeek: [1],
    monthOfYear: 1,
    invalidDatePolicy: 'last_day_of_month',
    startsOn: today,
    endsOn: '',
    accountId: '',
    destinationAccountId: '',
    categoryId: '',
    certainty: 'expected',
    notes: '',
  }
}

export function formToPattern(form: RecurringFormModel): RecurrencePatternInput {
  if (form.frequency === 'daily') {
    return { frequency: 'daily', interval: form.interval }
  }
  if (form.frequency === 'weekly') {
    return {
      frequency: 'weekly',
      interval: form.interval,
      daysOfWeek: form.daysOfWeek.length ? form.daysOfWeek : [1],
    }
  }
  if (form.frequency === 'yearly') {
    return {
      frequency: 'yearly',
      interval: form.interval,
      monthOfYear: form.monthOfYear ?? 1,
      dayOfMonth: form.endOfMonth ? null : form.dayOfMonth,
      endOfMonth: form.endOfMonth,
      invalidDatePolicy: form.invalidDatePolicy,
    }
  }
  return {
    frequency: 'monthly',
    interval: form.interval,
    dayOfMonth: form.endOfMonth ? null : form.dayOfMonth,
    endOfMonth: form.endOfMonth,
    invalidDatePolicy: form.invalidDatePolicy,
  }
}

export function useRecurringForm() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()

  const defaultCurrency = computed(
    () => organization.currentOrganization?.currency || 'MXN',
  )
  const form = ref<RecurringFormModel>(emptyForm(defaultCurrency.value))
  const accounts = ref<AccountSummary[]>([])
  const categories = ref<CategoryTreeNodeView[]>([])
  const submitting = ref(false)
  const previewLoading = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<Record<string, string>>({})
  const preview = ref<RecurringPreviewView | null>(null)

  const currencyOptions = computed(() => {
    const set = new Set(accounts.value.map(a => a.currency))
    set.add(defaultCurrency.value)
    return [...set]
  })

  function reset() {
    form.value = emptyForm(defaultCurrency.value)
    fieldErrors.value = {}
    error.value = null
    preview.value = null
  }

  async function loadLookups() {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    const [accountList, categoryTree] = await Promise.all([
      createAccountsRepository($api).list(orgId, { includeArchived: false }),
      createCategoriesRepository($api).list(orgId, { tree: true }),
    ])
    accounts.value = accountList
    categories.value = categoryTree
  }

  function validate(): boolean {
    const errors: Record<string, string> = {}
    if (!form.value.name.trim()) errors.name = 'El nombre es obligatorio.'
    if (!form.value.amount || Number(form.value.amount) <= 0) {
      errors.amount = 'Ingresa un monto mayor a cero.'
    }
    if (!form.value.startsOn) errors.startsOn = 'Selecciona la fecha de inicio.'
    if (form.value.direction === 'transfer') {
      if (!form.value.accountId) errors.accountId = 'Selecciona la cuenta origen.'
      if (!form.value.destinationAccountId) {
        errors.destinationAccountId = 'Selecciona la cuenta destino.'
      }
      if (
        form.value.accountId
        && form.value.destinationAccountId
        && form.value.accountId === form.value.destinationAccountId
      ) {
        errors.destinationAccountId = 'Origen y destino deben ser distintas.'
      }
    }
    if (form.value.frequency === 'monthly' && !form.value.endOfMonth && !form.value.dayOfMonth) {
      errors.dayOfMonth = 'Indica el día del mes o el último día.'
    }
    if (form.value.frequency === 'weekly' && !form.value.daysOfWeek.length) {
      errors.daysOfWeek = 'Selecciona al menos un día.'
    }
    fieldErrors.value = errors
    return Object.keys(errors).length === 0
  }

  function toCreateInput(): CreateRecurringRuleInput {
    return {
      name: form.value.name.trim(),
      direction: form.value.direction,
      amount: form.value.amount,
      currency: form.value.currency,
      pattern: formToPattern(form.value),
      startsOn: form.value.startsOn,
      endsOn: form.value.endsOn || null,
      certainty: form.value.certainty,
      accountId: form.value.accountId || null,
      destinationAccountId: form.value.destinationAccountId || null,
      categoryId: form.value.categoryId || null,
      notes: form.value.notes.trim() || null,
    }
  }

  async function runPreview() {
    const orgId = organization.currentOrganizationId
    if (!orgId || !form.value.startsOn) return
    previewLoading.value = true
    try {
      const from = form.value.startsOn
      const toAnchor = new Date(`${form.value.startsOn}T12:00:00`)
      toAnchor.setMonth(toAnchor.getMonth() + 3)
      const to = todayLocalIsoDate(toAnchor)
      const repo = createRecurringRepository($api)
      preview.value = await repo.preview(orgId, {
        name: form.value.name || 'Preview',
        direction: form.value.direction,
        amount: form.value.amount || '1.00',
        currency: form.value.currency,
        pattern: formToPattern(form.value),
        startsOn: form.value.startsOn,
        endsOn: form.value.endsOn || null,
        from,
        to,
        certainty: form.value.certainty,
      })
    }
    catch (e) {
      preview.value = null
      error.value = toUserMessage(e)
    }
    finally {
      previewLoading.value = false
    }
  }

  async function submitCreate(): Promise<string | null> {
    error.value = null
    if (!validate()) return null
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      return null
    }
    submitting.value = true
    try {
      const repo = createRecurringRepository($api)
      const created = await repo.create(orgId, toCreateInput())
      cache.invalidateRecurring()
      return created.id
    }
    catch (e) {
      error.value = toUserMessage(e)
      return null
    }
    finally {
      submitting.value = false
    }
  }

  return {
    form,
    accounts,
    categories,
    currencyOptions,
    submitting,
    previewLoading,
    error,
    fieldErrors,
    preview,
    reset,
    loadLookups,
    validate,
    runPreview,
    submitCreate,
  }
}
