/** UI-facing account types for onboarding V1. */
export type SimplifiedAccountType =
  | 'checking'
  | 'savings'
  | 'cash'
  | 'credit_card'
  | 'other'

/** Backend account_type values used in V1 onboarding. */
export type BackendAccountType = SimplifiedAccountType

const SIMPLIFIED_TO_BACKEND: Record<SimplifiedAccountType, BackendAccountType> = {
  checking: 'checking',
  savings: 'savings',
  cash: 'cash',
  credit_card: 'credit_card',
  other: 'other',
}

const BACKEND_TO_SIMPLIFIED: Record<string, SimplifiedAccountType> = {
  checking: 'checking',
  savings: 'savings',
  cash: 'cash',
  credit_card: 'credit_card',
  other: 'other',
  investment: 'other',
  digital_wallet: 'other',
  loan: 'other',
}

export function toBackendAccountType(
  simplified: SimplifiedAccountType,
): BackendAccountType {
  return SIMPLIFIED_TO_BACKEND[simplified]
}

export function toSimplifiedAccountType(backend: string): SimplifiedAccountType {
  return BACKEND_TO_SIMPLIFIED[backend] ?? 'other'
}

/**
 * Credit cards: the user enters a positive debt amount;
 * the API expects a negative opening_balance.
 * Money stays as decimal strings (no Number math).
 */
export function toOpeningBalancePayload(
  simplifiedType: SimplifiedAccountType,
  userEnteredAmount: string,
): string {
  const raw = userEnteredAmount.trim() || '0'
  const normalized = raw.replace(/,/g, '')
  const unsigned = normalized.replace(/^[+-]/, '') || '0'
  const amount = unsigned.includes('.') ? unsigned : `${unsigned}.00`

  if (simplifiedType !== 'credit_card') {
    return amount
  }

  if (amount === '0' || amount === '0.00' || /^0+\.0+$/.test(amount)) {
    return '0.00'
  }

  return `-${amount}`
}

export const SIMPLIFIED_ACCOUNT_TYPE_OPTIONS: Array<{
  value: SimplifiedAccountType
  label: string
  description: string
}> = [
  {
    value: 'checking',
    label: 'Cuenta bancaria',
    description: 'Cuenta de uso diario',
  },
  {
    value: 'savings',
    label: 'Ahorro',
    description: 'Cuenta o reserva de ahorro',
  },
  {
    value: 'cash',
    label: 'Efectivo',
    description: 'Dinero en mano o caja',
  },
  {
    value: 'credit_card',
    label: 'Tarjeta de crédito',
    description: 'Saldo que debes actualmente',
  },
  {
    value: 'other',
    label: 'Otra',
    description: 'Cualquier otro tipo de cuenta',
  },
]
