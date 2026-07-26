import { createAccountsRepository } from '~/repositories/accounts.repository'
import type {
  CreateAccountFormModel,
  UpdateAccountFormModel,
} from '~/types/accounts'
import {
  getAccountTypeOption,
  toOpeningBalancePayload,
  type BackendAccountType,
} from '~/utils/account-type-mapper'
import { toUserMessage } from '~/lib/api/errors'
import { todayLocalIsoDate } from '~/composables/use-date'

const CURRENCY_OPTIONS = [
  { label: 'MXN — Peso mexicano', value: 'MXN' },
  { label: 'USD — Dólar estadounidense', value: 'USD' },
  { label: 'EUR — Euro', value: 'EUR' },
]

export function useAccountForm(mode: 'create' | 'edit' = 'create') {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()
  const toast = useToast()

  const form = reactive<CreateAccountFormModel>({
    name: '',
    accountType: 'checking',
    currency: organization.currentOrganization?.currency || 'MXN',
    openingBalance: '0.00',
    openingBalanceDate: todayLocalIsoDate(),
    institutionName: '',
    lastFour: '',
  })

  const editForm = reactive<UpdateAccountFormModel>({
    name: '',
    institutionName: '',
    lastFour: '',
  })

  const submitting = ref(false)
  const error = ref<string | null>(null)
  const fieldErrors = ref<Record<string, string>>({})

  const balanceLabel = computed(() =>
    getAccountTypeOption(form.accountType).balanceLabel,
  )

  const typeOption = computed(() => getAccountTypeOption(form.accountType))

  const currencyOptions = CURRENCY_OPTIONS

  function clearFieldErrors() {
    fieldErrors.value = {}
  }

  function resetCreate(defaults?: Partial<CreateAccountFormModel>) {
    form.name = defaults?.name ?? ''
    form.accountType = defaults?.accountType ?? 'checking'
    form.currency = defaults?.currency
      ?? organization.currentOrganization?.currency
      ?? 'MXN'
    form.openingBalance = defaults?.openingBalance ?? '0.00'
    form.openingBalanceDate = defaults?.openingBalanceDate ?? todayLocalIsoDate()
    form.institutionName = defaults?.institutionName ?? ''
    form.lastFour = defaults?.lastFour ?? ''
    error.value = null
    clearFieldErrors()
  }

  function loadEdit(account: {
    name: string
    institutionName?: string | null
    lastFour?: string | null
  }) {
    editForm.name = account.name
    editForm.institutionName = account.institutionName ?? ''
    editForm.lastFour = account.lastFour ?? ''
    error.value = null
    clearFieldErrors()
  }

  function validateCreate(): boolean {
    clearFieldErrors()
    const next: Record<string, string> = {}
    if (!form.name.trim() || form.name.trim().length < 2) {
      next.name = 'El nombre debe tener al menos 2 caracteres.'
    }
    if (form.lastFour && !/^\d{4}$/.test(form.lastFour)) {
      next.lastFour = 'Deben ser exactamente 4 dígitos.'
    }
    if (!form.openingBalanceDate) {
      next.openingBalanceDate = 'Indica la fecha del saldo.'
    }
    const amount = form.openingBalance.trim().replace(/,/g, '')
    if (!/^-?\d+(\.\d{1,2})?$/.test(amount) && amount !== '') {
      next.openingBalance = 'Ingresa un monto válido.'
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
    if (editForm.lastFour && !/^\d{4}$/.test(editForm.lastFour)) {
      next.lastFour = 'Deben ser exactamente 4 dígitos.'
    }
    fieldErrors.value = next
    return Object.keys(next).length === 0
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
      const repo = createAccountsRepository($api)
      const account = await repo.create(orgId, {
        name: form.name.trim(),
        accountType: form.accountType,
        currency: form.currency,
        openingBalance: toOpeningBalancePayload(form.accountType, form.openingBalance),
        openingBalanceDate: form.openingBalanceDate || null,
        institutionName: form.institutionName.trim() || null,
        lastFour: form.lastFour.trim() || null,
      })
      cache.invalidateAccounts()
      toast.success('Cuenta creada', account.name)
      return account.id
    } catch (e) {
      error.value = toUserMessage(e)
      return null
    } finally {
      submitting.value = false
    }
  }

  async function submitEdit(accountId: string): Promise<boolean> {
    error.value = null
    if (!validateEdit()) return false

    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      return false
    }

    submitting.value = true
    try {
      const repo = createAccountsRepository($api)
      await repo.update(orgId, accountId, {
        name: editForm.name.trim(),
        institutionName: editForm.institutionName.trim() || null,
        lastFour: editForm.lastFour.trim() || null,
      })
      cache.invalidateAccounts()
      toast.success('Cuenta actualizada')
      return true
    } catch (e) {
      error.value = toUserMessage(e)
      return false
    } finally {
      submitting.value = false
    }
  }

  function setAccountType(type: BackendAccountType) {
    form.accountType = type
  }

  return {
    mode,
    form,
    editForm,
    submitting,
    error,
    fieldErrors,
    balanceLabel,
    typeOption,
    currencyOptions,
    resetCreate,
    loadEdit,
    validateCreate,
    validateEdit,
    submitCreate,
    submitEdit,
    setAccountType,
  }
}
