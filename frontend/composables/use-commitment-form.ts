import { createAccountsRepository } from '~/repositories/accounts.repository'
import { createCommitmentsRepository } from '~/repositories/commitments.repository'
import type {
  CommitmentAccountOption,
  CommitmentDetailView,
  CommitmentType,
  CreateCommitmentFormModel,
  UpdateCommitmentFormModel,
} from '~/types/commitments'
import { toUserMessage } from '~/lib/api/errors'
import { getAccountHintForType } from '~/utils/commitment-types'
import { track } from '~/utils/track'

const CURRENCY_OPTIONS = [
  { label: 'MXN — Peso mexicano', value: 'MXN' },
  { label: 'USD — Dólar estadounidense', value: 'USD' },
  { label: 'EUR — Euro', value: 'EUR' },
]

function normalizeAmount(raw: string): string | null {
  const trimmed = raw.trim().replace(/,/g, '')
  if (!trimmed) return null
  if (!/^\d+(\.\d{1,2})?$/.test(trimmed)) return null
  const [whole = '0', frac = ''] = trimmed.split('.')
  return `${whole}.${(frac + '00').slice(0, 2)}`
}

function emptyCreate(): CreateCommitmentFormModel {
  return {
    name: '',
    debtType: 'credit_card',
    creditor: '',
    priority: 'medium',
    accountId: '',
    createAccountInline: false,
    newAccountName: '',
    newAccountType: 'credit_card',
    newAccountOpeningBalance: '',
    currency: 'MXN',
    interestRate: '',
    minimumPayment: '',
    scheduledPayment: '',
    creditLimit: '',
    dueDay: '',
    statementDay: '',
    notes: '',
  }
}

export function useCommitmentForm(mode: 'create' | 'edit' = 'create') {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()
  const toast = useToast()

  const form = reactive<CreateCommitmentFormModel>({
    ...emptyCreate(),
    currency: organization.currentOrganization?.currency || 'MXN',
  })

  const editForm = reactive<UpdateCommitmentFormModel>({
    name: '',
    creditor: '',
    priority: 'medium',
    interestRate: '',
    minimumPayment: '',
    scheduledPayment: '',
    creditLimit: '',
    dueDay: '',
    statementDay: '',
    notes: '',
    version: 1,
  })

  const editMeta = reactive<{
    currency: string
    debtType: CommitmentType
    status: string
    accountId: string
  }>({
    currency: 'MXN',
    debtType: 'credit_card',
    status: 'active',
    accountId: '',
  })

  const accounts = ref<CommitmentAccountOption[]>([])
  const accountsLoading = ref(false)
  const submitting = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<Record<string, string>>({})

  const currencyOptions = CURRENCY_OPTIONS

  const liabilityAccounts = computed(() => {
    const currency = mode === 'create' ? form.currency : editMeta.currency
    return accounts.value.filter(
      a => a.classification === 'liability' && a.currency === currency,
    )
  })

  function resetCreate(defaults?: Partial<CreateCommitmentFormModel>) {
    Object.assign(form, emptyCreate(), {
      currency: organization.currentOrganization?.currency || 'MXN',
      ...defaults,
    })
    error.value = null
    fieldErrors.value = {}
  }

  function loadEdit(item: CommitmentDetailView) {
    editForm.name = item.name
    editForm.creditor = item.creditor ?? ''
    editForm.priority = item.priority
    editForm.interestRate = item.interestRate ?? ''
    editForm.minimumPayment = item.minimumPayment ?? ''
    editForm.scheduledPayment = item.scheduledPayment ?? ''
    editForm.creditLimit = item.creditLimit ?? ''
    editForm.dueDay = item.dueDay != null ? String(item.dueDay) : ''
    editForm.statementDay = item.statementDay != null ? String(item.statementDay) : ''
    editForm.notes = item.notes ?? ''
    editForm.version = item.version
    editMeta.currency = item.currency
    editMeta.debtType = item.debtType
    editMeta.status = item.status
    editMeta.accountId = item.accountId
    error.value = null
    fieldErrors.value = {}
  }

  async function loadAccounts() {
    const orgId = organization.currentOrganizationId
    if (!orgId) return
    accountsLoading.value = true
    try {
      const repo = createAccountsRepository($api)
      const list = await repo.list(orgId)
      accounts.value = list
        .filter(a => a.isActive)
        .map(a => ({
          id: a.id,
          name: a.name,
          currency: a.currency,
          currentBalance: a.currentBalance,
          accountType: a.accountType,
          classification: a.classification,
        }))
    }
    catch (e) {
      error.value = toUserMessage(e)
    }
    finally {
      accountsLoading.value = false
    }
  }

  function onDebtTypeChange(type: string) {
    const next = type as CommitmentType
    form.debtType = next
    form.newAccountType = getAccountHintForType(next)
  }

  function validateCreate(): boolean {
    const errors: Record<string, string> = {}
    if (form.name.trim().length < 2) errors.name = 'El nombre debe tener al menos 2 caracteres.'
    if (!form.createAccountInline && !form.accountId) {
      errors.accountId = 'Selecciona una cuenta de pasivo.'
    }
    if (form.createAccountInline && form.newAccountName.trim().length < 2) {
      errors.newAccountName = 'Nombre de cuenta requerido.'
    }
    if (form.dueDay && (Number(form.dueDay) < 1 || Number(form.dueDay) > 31)) {
      errors.dueDay = 'Día entre 1 y 31.'
    }
    if (form.interestRate && normalizeAmount(form.interestRate) == null) {
      errors.interestRate = 'Tasa inválida.'
    }
    if (form.minimumPayment && normalizeAmount(form.minimumPayment) == null) {
      errors.minimumPayment = 'Monto inválido.'
    }
    fieldErrors.value = errors
    return Object.keys(errors).length === 0
  }

  function validateEdit(): boolean {
    const errors: Record<string, string> = {}
    if (editForm.name.trim().length < 2) errors.name = 'El nombre debe tener al menos 2 caracteres.'
    if (editForm.dueDay && (Number(editForm.dueDay) < 1 || Number(editForm.dueDay) > 31)) {
      errors.dueDay = 'Día entre 1 y 31.'
    }
    fieldErrors.value = errors
    return Object.keys(errors).length === 0
  }

  async function submitCreate(): Promise<string | null> {
    const orgId = organization.currentOrganizationId
    if (!orgId || !validateCreate()) return null

    submitting.value = true
    error.value = null
    try {
      let accountId = form.accountId
      if (form.createAccountInline) {
        const accountsRepo = createAccountsRepository($api)
        const opening = normalizeAmount(form.newAccountOpeningBalance) ?? '0.00'
        // Liability opening: store as negative if user enters positive owed amount
        const openingSigned = opening === '0.00'
          ? '0.00'
          : opening.startsWith('-')
            ? opening
            : `-${opening}`
        const account = await accountsRepo.create(orgId, {
          name: form.newAccountName.trim(),
          accountType: form.newAccountType,
          currency: form.currency,
          openingBalance: openingSigned,
        })
        accountId = account.id
        cache.invalidateAccounts()
      }

      const repo = createCommitmentsRepository($api)
      const created = await repo.create(orgId, {
        accountId,
        name: form.name.trim(),
        debtType: form.debtType,
        creditor: form.creditor.trim() || null,
        priority: form.priority,
        interestRate: normalizeAmount(form.interestRate),
        minimumPayment: normalizeAmount(form.minimumPayment),
        scheduledPayment: normalizeAmount(form.scheduledPayment),
        creditLimit: normalizeAmount(form.creditLimit),
        dueDay: form.dueDay ? Number(form.dueDay) : null,
        statementDay: form.statementDay ? Number(form.statementDay) : null,
        notes: form.notes.trim() || null,
      })
      cache.invalidateCommitments()
      track('commitment_created', {
        commitment_type: created.debtType,
        source_screen: 'commitments_new',
        success: true,
      })
      toast.success('Obligación creada', created.name)
      return created.id
    }
    catch (e) {
      error.value = toUserMessage(e)
      track('commitment_created_failed', {
        commitment_type: form.debtType,
        source_screen: 'commitments_new',
        success: false,
        error_code: 'create_failed',
      })
      toast.error('No se pudo crear', toUserMessage(e))
      return null
    }
    finally {
      submitting.value = false
    }
  }

  async function submitEdit(commitmentId: string): Promise<boolean> {
    const orgId = organization.currentOrganizationId
    if (!orgId || !validateEdit()) return false

    submitting.value = true
    error.value = null
    try {
      const repo = createCommitmentsRepository($api)
      const updated = await repo.update(orgId, commitmentId, {
        name: editForm.name.trim(),
        creditor: editForm.creditor.trim() || null,
        priority: editForm.priority,
        interestRate: normalizeAmount(editForm.interestRate),
        minimumPayment: normalizeAmount(editForm.minimumPayment),
        scheduledPayment: normalizeAmount(editForm.scheduledPayment),
        creditLimit: normalizeAmount(editForm.creditLimit),
        dueDay: editForm.dueDay ? Number(editForm.dueDay) : null,
        statementDay: editForm.statementDay ? Number(editForm.statementDay) : null,
        notes: editForm.notes.trim() || null,
        version: editForm.version,
      })
      editForm.version = updated.version
      cache.invalidateCommitments()
      toast.success('Obligación actualizada')
      return true
    }
    catch (e) {
      error.value = toUserMessage(e)
      toast.error('No se pudo guardar', toUserMessage(e))
      return false
    }
    finally {
      submitting.value = false
    }
  }

  return {
    form,
    editForm,
    editMeta,
    accounts,
    liabilityAccounts,
    accountsLoading,
    submitting,
    error,
    fieldErrors,
    currencyOptions,
    resetCreate,
    loadEdit,
    loadAccounts,
    onDebtTypeChange,
    submitCreate,
    submitEdit,
  }
}
