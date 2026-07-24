import { createAccountsRepository } from '~/repositories/accounts.repository'
import type {
  AccountCurrencySummaryView,
  AccountFilterChip,
  AccountGroupView,
  AccountListItemView,
} from '~/types/accounts'
import type { AccountSummary } from '~/types/domain'
import {
  ACCOUNT_GROUP_ORDER,
  presentAccount,
  type AccountGroupKey,
  type BackendAccountType,
} from '~/utils/account-type-mapper'
import {
  absDecimalString,
  addDecimalStrings,
} from '~/utils/decimal-string'
import { toUserMessage } from '~/lib/api/errors'

export function toListItem(account: AccountSummary): AccountListItemView {
  const presentation = presentAccount({
    accountType: account.accountType,
    currentBalance: account.currentBalance,
    currency: account.currency,
    isActive: account.isActive,
    institutionName: account.institutionName,
    name: account.name,
  })

  return {
    id: account.id,
    name: account.name,
    displayType: presentation.displayType,
    type: account.accountType as BackendAccountType,
    group: presentation.group,
    groupLabel: presentation.groupLabel,
    currency: account.currency,
    ledgerBalance: presentation.ledgerBalance,
    balance: presentation.displayBalance,
    balanceLabel: presentation.balanceLabel,
    balancePresentation: presentation.balancePresentation,
    balancePrefix: presentation.balancePrefix,
    institution: account.institutionName ?? undefined,
    lastFour: account.lastFour ?? undefined,
    isLiquid: presentation.isLiquid,
    isArchived: presentation.isArchived,
    subtitle: presentation.subtitle,
    updatedAt: account.updatedAt,
    createdAt: account.createdAt,
    archivedAt: account.archivedAt ?? undefined,
  }
}

/** Currency summaries — never mix currencies. Liabilities shown as negative. */
export function computeCurrencySummaries(
  accounts: AccountListItemView[],
): AccountCurrencySummaryView[] {
  const active = accounts.filter(a => !a.isArchived)
  const currencies = [...new Set(active.map(a => a.currency))].sort()

  return currencies.map((currency) => {
    const inCurrency = active.filter(a => a.currency === currency)

    const liquidAssets = addDecimalStrings(
      ...inCurrency
        .filter(a => a.isLiquid && a.balancePresentation === 'asset')
        .map(a => a.ledgerBalance),
      '0.00',
    )

    const savings = addDecimalStrings(
      ...inCurrency
        .filter(a => a.type === 'savings')
        .map(a => a.ledgerBalance),
      '0.00',
    )

    const investments = addDecimalStrings(
      ...inCurrency
        .filter(a => a.type === 'investment')
        .map(a => a.ledgerBalance),
      '0.00',
    )

    const liabilityLedger = addDecimalStrings(
      ...inCurrency
        .filter(a => a.type === 'credit_card' || a.type === 'loan')
        .map(a => a.ledgerBalance),
      '0.00',
    )
    const liabilitiesAbs = absDecimalString(liabilityLedger)
    const liabilities = liabilitiesAbs === '0.00' ? '0.00' : `-${liabilitiesAbs}`

    const assetTotal = addDecimalStrings(
      ...inCurrency
        .filter(a => a.balancePresentation === 'asset')
        .map(a => a.ledgerBalance),
      '0.00',
    )
    const netWorth = addDecimalStrings(assetTotal, liabilityLedger)

    return {
      currency,
      liquidAssets,
      savings,
      investments,
      liabilities,
      netWorth,
    }
  })
}

function matchesFilter(account: AccountListItemView, chip: AccountFilterChip): boolean {
  switch (chip) {
    case 'all':
      return !account.isArchived
    case 'cash':
      return !account.isArchived && account.group === 'cash_banks'
    case 'savings':
      return !account.isArchived && account.group === 'savings'
    case 'investments':
      return !account.isArchived && account.group === 'investments'
    case 'debts':
      return !account.isArchived && account.group === 'credit_debts'
    case 'archived':
      return account.isArchived
    default:
      return true
  }
}

export function useAccounts() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()

  const accounts = ref<AccountListItemView[]>([])
  const listLoading = ref(false)
  const summaryLoading = ref(false)
  const listError = ref<string | null>(null)
  const summaryError = ref<string | null>(null)

  const filterChip = ref<AccountFilterChip>('all')
  const search = ref('')
  const currencyFilter = ref<string | null>(null)

  const currencySummaries = computed(() => computeCurrencySummaries(accounts.value))

  const availableCurrencies = computed(() =>
    [...new Set(accounts.value.filter(a => !a.isArchived).map(a => a.currency))].sort(),
  )

  const filteredAccounts = computed(() => {
    const q = search.value.trim().toLowerCase()
    return accounts.value.filter((account) => {
      if (!matchesFilter(account, filterChip.value)) return false
      if (currencyFilter.value && account.currency !== currencyFilter.value) return false
      if (!q) return true
      return (
        account.name.toLowerCase().includes(q)
        || (account.institution?.toLowerCase().includes(q) ?? false)
        || account.displayType.toLowerCase().includes(q)
      )
    })
  })

  const groups = computed<AccountGroupView[]>(() => {
    const byGroup = new Map<AccountGroupKey, AccountListItemView[]>()
    for (const account of filteredAccounts.value) {
      const list = byGroup.get(account.group) ?? []
      list.push(account)
      byGroup.set(account.group, list)
    }

    return ACCOUNT_GROUP_ORDER
      .filter(key => (byGroup.get(key)?.length ?? 0) > 0)
      .map(key => ({
        key,
        label: byGroup.get(key)![0].groupLabel,
        accounts: byGroup.get(key)!,
      }))
  })

  const hasAnyAccounts = computed(() => accounts.value.length > 0)
  const hasActiveAccounts = computed(() => accounts.value.some(a => !a.isArchived))

  async function load() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      listError.value = 'Selecciona una organización.'
      summaryError.value = listError.value
      accounts.value = []
      return
    }

    listLoading.value = true
    summaryLoading.value = true
    listError.value = null
    summaryError.value = null

    try {
      const repo = createAccountsRepository($api)
      const raw = await repo.list(orgId, { includeArchived: true })
      accounts.value = raw.map(toListItem)
    } catch (e) {
      const message = toUserMessage(e)
      listError.value = message
      summaryError.value = message
      accounts.value = []
    } finally {
      listLoading.value = false
      summaryLoading.value = false
    }
  }

  watch(
    () => cache.accountsVersion.value,
    () => {
      void load()
    },
  )

  return {
    accounts,
    listLoading,
    summaryLoading,
    listError,
    summaryError,
    filterChip,
    search,
    currencyFilter,
    currencySummaries,
    availableCurrencies,
    filteredAccounts,
    groups,
    hasAnyAccounts,
    hasActiveAccounts,
    load,
    toListItem,
  }
}
