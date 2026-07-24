import type {
  AccountGroupKey,
  BackendAccountType,
  BalancePresentation,
} from '~/utils/account-type-mapper'

export type AccountFilterChip =
  | 'all'
  | 'cash'
  | 'savings'
  | 'investments'
  | 'debts'
  | 'archived'

export interface AccountFilters {
  includeArchived?: boolean
}

export interface AccountListItemView {
  id: string
  name: string
  displayType: string
  type: BackendAccountType
  group: AccountGroupKey
  groupLabel: string
  currency: string
  /** Signed ledger balance. */
  ledgerBalance: string
  /** Positive magnitude for display. */
  balance: string
  balanceLabel: string
  balancePresentation: BalancePresentation
  balancePrefix: string | null
  institution?: string
  lastFour?: string
  isLiquid: boolean
  isArchived: boolean
  subtitle: string
  updatedAt?: string
  createdAt?: string
  archivedAt?: string
}

export interface AccountCurrencySummaryView {
  currency: string
  liquidAssets: string
  savings: string
  investments: string
  liabilities: string
  netWorth: string
}

export interface AccountGroupView {
  key: AccountGroupKey
  label: string
  accounts: AccountListItemView[]
}

export interface CreateAccountFormModel {
  name: string
  accountType: BackendAccountType
  currency: string
  openingBalance: string
  openingBalanceDate: string
  institutionName: string
  lastFour: string
}

export interface UpdateAccountFormModel {
  name: string
  institutionName: string
  lastFour: string
}

export interface UpdateAccountInput {
  name?: string
  institutionName?: string | null
  lastFour?: string | null
}
