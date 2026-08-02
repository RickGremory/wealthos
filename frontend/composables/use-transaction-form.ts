import { createTransactionsRepository } from '~/repositories/transactions.repository'
import type {
  TransactionDetailView,
  TransactionDuplicateDraft,
  TransactionFormModel,
  TransactionType,
} from '~/types/transactions'
import type { AccountSummary } from '~/types/domain'
import { toUserMessage } from '~/lib/api/errors'
import {
  buildCreateTransactionPayload,
  emptyTransactionForm,
  todayDateInputValue,
  validateTransactionForm,
} from '~/utils/transaction-payload'
import { useTransactionIdempotency } from '~/composables/use-transaction-idempotency'

export function useTransactionForm(options?: {
  accounts?: Ref<AccountSummary[]> | ComputedRef<AccountSummary[]>
  categoryNameResolver?: (categoryId: string) => string | null
}) {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()
  const idempotency = useTransactionIdempotency()

  const form = ref<TransactionFormModel>(emptyTransactionForm('expense'))
  const submitting = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<Record<string, string>>({})
  const created = ref<TransactionDetailView | null>(null)

  const accounts = computed(() => options?.accounts?.value ?? [])

  const selectedAccount = computed(() =>
    accounts.value.find(a => a.id === form.value.accountId) ?? null,
  )

  const sourceAccount = computed(() =>
    accounts.value.find(a => a.id === form.value.sourceAccountId) ?? null,
  )

  const destinationAccount = computed(() =>
    accounts.value.find(a => a.id === form.value.destinationAccountId) ?? null,
  )

  const currencyMismatch = computed(() => {
    if (form.value.type !== 'transfer') return false
    if (!sourceAccount.value || !destinationAccount.value) return false
    return sourceAccount.value.currency !== destinationAccount.value.currency
  })

  function reset(type: TransactionType = 'expense') {
    form.value = emptyTransactionForm(type)
    fieldErrors.value = {}
    error.value = null
    created.value = null
    idempotency.renew()
  }

  function setType(type: TransactionType) {
    const prev = form.value.type
    if (prev === type) return
    form.value.type = type
    // Reset incompatible fields
    if (type === 'transfer') {
      form.value.accountId = ''
      form.value.categoryId = ''
      form.value.realBalance = ''
    } else if (type === 'adjustment') {
      form.value.sourceAccountId = ''
      form.value.destinationAccountId = ''
      form.value.amount = ''
      form.value.categoryId = ''
    } else {
      form.value.sourceAccountId = ''
      form.value.destinationAccountId = ''
      form.value.realBalance = ''
      if (prev === 'income' || prev === 'expense') {
        form.value.categoryId = ''
      }
    }
    fieldErrors.value = {}
    error.value = null
  }

  function applyDuplicateDraft(draft: Partial<TransactionDuplicateDraft> | null) {
    const type = draft?.type ?? 'expense'
    reset(type)
    if (!draft) return
    form.value.occurredDate = draft.occurredDate || todayDateInputValue()
    if (draft.amount) form.value.amount = draft.amount
    if (draft.description) form.value.description = draft.description
    if (draft.notes) form.value.notes = draft.notes
    if (draft.accountId) form.value.accountId = draft.accountId
    if (draft.categoryId) form.value.categoryId = draft.categoryId
    if (draft.sourceAccountId) form.value.sourceAccountId = draft.sourceAccountId
    if (draft.destinationAccountId) {
      form.value.destinationAccountId = draft.destinationAccountId
    }
  }

  function validate(): boolean {
    const currentBalance = selectedAccount.value?.currentBalance ?? '0.00'
    const errors = validateTransactionForm(form.value, { currentBalance })
    if (currencyMismatch.value) {
      errors.push({
        field: 'destinationAccountId',
        message: 'Las cuentas deben tener la misma moneda.',
      })
    }
    const map: Record<string, string> = {}
    for (const e of errors) map[e.field] = e.message
    fieldErrors.value = map
    return errors.length === 0
  }

  async function submit(): Promise<TransactionDetailView | null> {
    error.value = null
    created.value = null
    if (!validate()) return null

    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      return null
    }

    submitting.value = true
    try {
      const composer = useTransactionComposerStore()
      const categoryName = form.value.categoryId
        ? options?.categoryNameResolver?.(form.value.categoryId) ?? null
        : null
      const payload = buildCreateTransactionPayload({
        form: form.value,
        currentBalance: selectedAccount.value?.currentBalance ?? '0.00',
        categoryName,
        source: composer.createSource,
      })
      const repo = createTransactionsRepository($api)
      const result = await repo.create(orgId, payload, idempotency.current())
      created.value = result
      cache.invalidateTransactions()
      idempotency.renew()
      return result
    } catch (e) {
      error.value = toUserMessage(e)
      return null
    } finally {
      submitting.value = false
    }
  }

  return {
    form,
    submitting,
    error,
    fieldErrors,
    created,
    selectedAccount,
    sourceAccount,
    destinationAccount,
    currencyMismatch,
    reset,
    setType,
    applyDuplicateDraft,
    validate,
    submit,
    idempotency,
  }
}
