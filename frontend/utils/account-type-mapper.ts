/**
 * Account presentation rules — labels, groups, balance language.
 * Money stays as decimal strings; no Number arithmetic for ledger values.
 */

export type BackendAccountType =
  | 'checking'
  | 'savings'
  | 'cash'
  | 'credit_card'
  | 'investment'
  | 'loan'
  | 'digital_wallet'
  | 'other'

export type AccountGroupKey =
  | 'cash_banks'
  | 'savings'
  | 'investments'
  | 'credit_debts'
  | 'other'
  | 'archived'

export type BalancePresentation = 'asset' | 'liability'

export interface AccountTypeOption {
  value: BackendAccountType
  label: string
  description: string
  balanceLabel: string
  group: Exclude<AccountGroupKey, 'archived'>
  presentation: BalancePresentation
  isLiquid: boolean
}

export const ACCOUNT_TYPE_OPTIONS: AccountTypeOption[] = [
  {
    value: 'checking',
    label: 'Cuenta bancaria',
    description: 'Cuenta de uso diario para gastos y depósitos.',
    balanceLabel: 'Saldo actual',
    group: 'cash_banks',
    presentation: 'asset',
    isLiquid: true,
  },
  {
    value: 'cash',
    label: 'Efectivo',
    description: 'Dinero en mano o caja.',
    balanceLabel: 'Saldo actual',
    group: 'cash_banks',
    presentation: 'asset',
    isLiquid: true,
  },
  {
    value: 'digital_wallet',
    label: 'Billetera digital',
    description: 'Saldo en apps o monederos electrónicos.',
    balanceLabel: 'Saldo actual',
    group: 'cash_banks',
    presentation: 'asset',
    isLiquid: true,
  },
  {
    value: 'savings',
    label: 'Cuenta de ahorro',
    description: 'Reserva o cuenta de ahorro.',
    balanceLabel: 'Saldo actual',
    group: 'savings',
    presentation: 'asset',
    isLiquid: false,
  },
  {
    value: 'investment',
    label: 'Inversión',
    description: 'Portafolio, fondos o instrumentos de inversión.',
    balanceLabel: 'Valor actual',
    group: 'investments',
    presentation: 'asset',
    isLiquid: false,
  },
  {
    value: 'credit_card',
    label: 'Tarjeta de crédito',
    description: 'Registra el saldo que debes actualmente.',
    balanceLabel: 'Saldo pendiente',
    group: 'credit_debts',
    presentation: 'liability',
    isLiquid: false,
  },
  {
    value: 'loan',
    label: 'Préstamo',
    description: 'Crédito o deuda con saldo pendiente.',
    balanceLabel: 'Saldo pendiente',
    group: 'credit_debts',
    presentation: 'liability',
    isLiquid: false,
  },
  {
    value: 'other',
    label: 'Otra',
    description: 'Cualquier otro tipo de cuenta.',
    balanceLabel: 'Saldo actual',
    group: 'other',
    presentation: 'asset',
    isLiquid: false,
  },
]

const BY_TYPE = Object.fromEntries(
  ACCOUNT_TYPE_OPTIONS.map(option => [option.value, option]),
) as Record<BackendAccountType, AccountTypeOption>

export const ACCOUNT_GROUP_LABELS: Record<AccountGroupKey, string> = {
  cash_banks: 'Efectivo y bancos',
  savings: 'Ahorro',
  investments: 'Inversiones',
  credit_debts: 'Crédito y deudas',
  other: 'Otras cuentas',
  archived: 'Archivadas',
}

export const ACCOUNT_GROUP_ORDER: AccountGroupKey[] = [
  'cash_banks',
  'savings',
  'investments',
  'credit_debts',
  'other',
  'archived',
]

export function normalizeAccountType(type: string): BackendAccountType {
  return (BY_TYPE[type as BackendAccountType] ? type : 'other') as BackendAccountType
}

export function getAccountTypeOption(type: string): AccountTypeOption {
  return BY_TYPE[normalizeAccountType(type)]
}

export function getAccountGroupKey(
  type: string,
  isArchived: boolean,
): AccountGroupKey {
  if (isArchived) return 'archived'
  return getAccountTypeOption(type).group
}

/** Absolute magnitude as a decimal string (no leading minus). */
export function absoluteDecimalString(value: string): string {
  const trimmed = value.trim() || '0'
  return trimmed.replace(/^[+-]/, '') || '0'
}

/**
 * User enters a positive amount in forms.
 * Liabilities are stored as negative opening balances in the ledger.
 */
export function toOpeningBalancePayload(
  accountType: string,
  userEnteredAmount: string,
): string {
  const raw = userEnteredAmount.trim() || '0'
  const normalized = raw.replace(/,/g, '')
  const unsigned = normalized.replace(/^[+-]/, '') || '0'
  const amount = unsigned.includes('.') ? unsigned : `${unsigned}.00`

  if (amount === '0' || amount === '0.00' || /^0+\.0+$/.test(amount)) {
    return '0.00'
  }

  const option = getAccountTypeOption(accountType)
  if (option.presentation === 'liability') {
    return `-${amount}`
  }
  return amount
}

export interface AccountPresentationInput {
  accountType: string
  currentBalance: string
  currency: string
  isActive: boolean
  institutionName?: string | null
  name: string
}

export interface AccountPresentation {
  displayType: string
  group: AccountGroupKey
  groupLabel: string
  balanceLabel: string
  balancePresentation: BalancePresentation
  /** Signed ledger value. */
  ledgerBalance: string
  /** Positive display magnitude for UI. */
  displayBalance: string
  /** Human phrase e.g. "Debes $8,500" context — amount only here. */
  balancePrefix: string | null
  isLiquid: boolean
  isArchived: boolean
  subtitle: string
}

export function presentAccount(input: AccountPresentationInput): AccountPresentation {
  const option = getAccountTypeOption(input.accountType)
  const isArchived = !input.isActive
  const group = getAccountGroupKey(input.accountType, isArchived)
  const ledgerBalance = input.currentBalance
  const displayBalance = absoluteDecimalString(ledgerBalance)

  let balancePrefix: string | null = null
  if (option.presentation === 'liability') {
    balancePrefix = option.value === 'loan' ? null : 'Debes'
  }

  const parts = [
    input.institutionName?.trim() || null,
    option.label,
  ].filter(Boolean)

  return {
    displayType: option.label,
    group,
    groupLabel: ACCOUNT_GROUP_LABELS[group],
    balanceLabel: option.balanceLabel,
    balancePresentation: option.presentation,
    ledgerBalance,
    displayBalance,
    balancePrefix,
    isLiquid: option.isLiquid && !isArchived,
    isArchived,
    subtitle: parts.join(' · '),
  }
}

/** @deprecated Prefer ACCOUNT_TYPE_OPTIONS / presentAccount. Kept for onboarding. */
export type SimplifiedAccountType =
  | 'checking'
  | 'savings'
  | 'cash'
  | 'credit_card'
  | 'other'

export function toBackendAccountType(
  simplified: SimplifiedAccountType,
): BackendAccountType {
  return simplified
}

export function toSimplifiedAccountType(backend: string): SimplifiedAccountType {
  const normalized = normalizeAccountType(backend)
  if (
    normalized === 'checking'
    || normalized === 'savings'
    || normalized === 'cash'
    || normalized === 'credit_card'
    || normalized === 'other'
  ) {
    return normalized
  }
  return 'other'
}

export const SIMPLIFIED_ACCOUNT_TYPE_OPTIONS = ACCOUNT_TYPE_OPTIONS.filter(option =>
  ['checking', 'savings', 'cash', 'credit_card', 'other'].includes(option.value),
).map(option => ({
  value: option.value as SimplifiedAccountType,
  label: option.label,
  description: option.description,
}))
