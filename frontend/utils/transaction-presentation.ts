/**
 * Presentation rules for transaction signs, labels, and liability language.
 */

export type TransactionType = 'income' | 'expense' | 'transfer' | 'adjustment'
export type TransactionStatus = 'posted' | 'voided'
export type PresentationSign = 'positive' | 'negative' | 'neutral'

export interface TransactionPresentation {
  typeLabel: string
  statusLabel: string
  presentationSign: PresentationSign
  /** Prefix for list amount display, e.g. "+" "-" or "" */
  amountPrefix: string
  impactHint?: string
}

const TYPE_LABELS: Record<TransactionType, string> = {
  income: 'Ingreso',
  expense: 'Gasto',
  transfer: 'Transferencia',
  adjustment: 'Ajuste',
}

const STATUS_LABELS: Record<TransactionStatus, string> = {
  posted: 'Registrado',
  voided: 'Anulado',
}

export function presentTransactionType(type: string): string {
  return TYPE_LABELS[type as TransactionType] ?? type
}

export function presentTransactionStatus(status: string): string {
  return STATUS_LABELS[status as TransactionStatus] ?? status
}

export function getPresentationSign(
  type: string,
  signedAmount?: string | null,
): PresentationSign {
  if (type === 'income') return 'positive'
  if (type === 'expense') return 'negative'
  if (type === 'transfer') return 'neutral'
  if (type === 'adjustment') {
    if (!signedAmount) return 'neutral'
    return signedAmount.trim().startsWith('-') ? 'negative' : 'positive'
  }
  return 'neutral'
}

export function presentTransaction(input: {
  type: string
  status: string
  signedAmount?: string | null
  accountType?: string | null
}): TransactionPresentation {
  const presentationSign = getPresentationSign(input.type, input.signedAmount)
  let amountPrefix = ''
  if (presentationSign === 'positive') amountPrefix = '+'
  if (presentationSign === 'negative') amountPrefix = '-'

  let impactHint: string | undefined
  if (input.type === 'expense' && input.accountType === 'credit_card') {
    impactHint = 'La deuda de esta tarjeta aumentará con este gasto.'
  } else if (input.type === 'expense' && input.accountType === 'loan') {
    impactHint = 'El saldo pendiente del préstamo aumentará.'
  }

  return {
    typeLabel: presentTransactionType(input.type),
    statusLabel: presentTransactionStatus(input.status),
    presentationSign,
    amountPrefix,
    impactHint,
  }
}

/** Absolute magnitude for UI when sign is conveyed separately. */
export function displayAmountMagnitude(amount: string | null | undefined): string {
  if (!amount) return '0.00'
  return amount.trim().replace(/^[+-]/, '') || '0.00'
}
