import { todayLocalIsoDate } from '~/composables/use-date'
import type {
  CreateTransactionInput,
  TransactionFormModel,
} from '~/types/transactions'
import {
  addDecimalStrings,
  isZeroDecimalString,
  negateDecimalString,
} from '~/utils/decimal-string'
import { displayAmountMagnitude } from '~/utils/transaction-presentation'

export interface BuildOccurredAtOptions {
  /** Local calendar date YYYY-MM-DD */
  date: string
  now?: Date
}

/** Noon local for past dates; "now" when the date is today. */
export function buildOccurredAtIso(options: BuildOccurredAtOptions): string {
  const now = options.now ?? new Date()
  const [y, m, d] = options.date.split('-').map(Number)
  if (!y || !m || !d) return now.toISOString()

  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const target = new Date(y, m - 1, d)
  const isToday
    = target.getFullYear() === today.getFullYear()
      && target.getMonth() === today.getMonth()
      && target.getDate() === today.getDate()

  if (isToday) return now.toISOString()

  const noon = new Date(y, m - 1, d, 12, 0, 0, 0)
  return noon.toISOString()
}

export function todayDateInputValue(now = new Date()): string {
  return todayLocalIsoDate(now)
}

export function normalizeUnsignedAmount(value: string): string {
  const mag = displayAmountMagnitude(value)
  if (!mag || mag === '0.00') return mag || '0.00'
  const [whole = '0', frac = ''] = mag.split('.')
  return `${whole || '0'}.${(frac + '00').slice(0, 2)}`
}

export function computeAdjustmentDelta(
  realBalance: string,
  currentBalance: string,
): string {
  return addDecimalStrings(realBalance || '0.00', negateDecimalString(currentBalance || '0.00'))
}

export interface BuildPayloadOptions {
  form: TransactionFormModel
  /** Required for adjustment delta */
  currentBalance?: string
  /** Category name used as default expense/income description */
  categoryName?: string | null
  now?: Date
}

export interface PayloadValidationError {
  field: string
  message: string
}

export function validateTransactionForm(
  form: TransactionFormModel,
  options?: { currentBalance?: string },
): PayloadValidationError[] {
  const errors: PayloadValidationError[] = []

  if (form.type === 'adjustment') {
    if (!form.accountId) {
      errors.push({ field: 'accountId', message: 'Selecciona una cuenta.' })
    }
    if (!form.realBalance.trim()) {
      errors.push({ field: 'realBalance', message: 'Ingresa el saldo real.' })
    }
    const delta = computeAdjustmentDelta(
      form.realBalance,
      options?.currentBalance ?? '0.00',
    )
    if (isZeroDecimalString(delta)) {
      errors.push({
        field: 'realBalance',
        message: 'El saldo real es igual al saldo actual; no hay ajuste.',
      })
    }
    if (form.description.trim().length < 2) {
      errors.push({ field: 'description', message: 'Indica el motivo (mínimo 2 caracteres).' })
    }
  } else {
    const amount = normalizeUnsignedAmount(form.amount)
    if (!amount || isZeroDecimalString(amount) || amount.startsWith('-')) {
      errors.push({ field: 'amount', message: 'Ingresa un monto mayor a cero.' })
    }

    if (form.type === 'transfer') {
      if (!form.sourceAccountId) {
        errors.push({ field: 'sourceAccountId', message: 'Selecciona la cuenta origen.' })
      }
      if (!form.destinationAccountId) {
        errors.push({
          field: 'destinationAccountId',
          message: 'Selecciona la cuenta destino.',
        })
      }
      if (
        form.sourceAccountId
        && form.destinationAccountId
        && form.sourceAccountId === form.destinationAccountId
      ) {
        errors.push({
          field: 'destinationAccountId',
          message: 'Origen y destino deben ser distintas.',
        })
      }
      if (form.description.trim().length < 2) {
        errors.push({
          field: 'description',
          message: 'La descripción debe tener al menos 2 caracteres.',
        })
      }
    } else {
      if (!form.accountId) {
        errors.push({ field: 'accountId', message: 'Selecciona una cuenta.' })
      }
      if (!form.categoryId) {
        errors.push({ field: 'categoryId', message: 'Selecciona una categoría.' })
      }
      const desc = form.description.trim()
      if (desc.length > 0 && desc.length < 2) {
        errors.push({
          field: 'description',
          message: 'La descripción debe tener al menos 2 caracteres.',
        })
      }
    }
  }

  if (!form.occurredDate) {
    errors.push({ field: 'occurredDate', message: 'Selecciona una fecha.' })
  }

  return errors
}

export function buildCreateTransactionPayload(
  options: BuildPayloadOptions,
): CreateTransactionInput {
  const { form, categoryName, now } = options
  const occurredAt = buildOccurredAtIso({ date: form.occurredDate, now })
  const notes = form.notes.trim() || null

  if (form.type === 'transfer') {
    return {
      transactionType: 'transfer',
      sourceAccountId: form.sourceAccountId,
      destinationAccountId: form.destinationAccountId,
      amount: normalizeUnsignedAmount(form.amount),
      description: form.description.trim() || 'Transferencia',
      occurredAt,
      notes,
    }
  }

  if (form.type === 'adjustment') {
    const delta = computeAdjustmentDelta(
      form.realBalance,
      options.currentBalance ?? '0.00',
    )
    return {
      transactionType: 'adjustment',
      accountId: form.accountId,
      amount: delta,
      description: form.description.trim(),
      occurredAt,
      categoryId: form.categoryId || null,
      notes,
    }
  }

  const description
    = form.description.trim()
      || (categoryName?.trim() && categoryName.trim().length >= 2
        ? categoryName.trim()
        : form.type === 'income'
          ? 'Ingreso'
          : 'Gasto')

  return {
    transactionType: form.type,
    accountId: form.accountId,
    categoryId: form.categoryId,
    amount: normalizeUnsignedAmount(form.amount),
    description,
    occurredAt,
    notes,
  }
}

/** API body (snake_case) for POST /transactions */
export function toApiCreateBody(input: CreateTransactionInput): Record<string, unknown> {
  const base = {
    description: input.description,
    occurred_at: input.occurredAt,
    notes: input.notes ?? null,
  }

  if (input.transactionType === 'transfer') {
    return {
      ...base,
      transaction_type: 'transfer',
      source_account_id: input.sourceAccountId,
      destination_account_id: input.destinationAccountId,
      amount: input.amount,
    }
  }

  if (input.transactionType === 'adjustment') {
    return {
      ...base,
      transaction_type: 'adjustment',
      account_id: input.accountId,
      amount: input.amount,
      category_id: input.categoryId ?? null,
    }
  }

  return {
    ...base,
    transaction_type: input.transactionType,
    account_id: input.accountId,
    category_id: input.categoryId,
    amount: input.amount,
  }
}

export function emptyTransactionForm(
  type: TransactionFormModel['type'] = 'expense',
  now = new Date(),
): TransactionFormModel {
  return {
    type,
    amount: '',
    description: '',
    notes: '',
    occurredDate: todayDateInputValue(now),
    accountId: '',
    categoryId: '',
    sourceAccountId: '',
    destinationAccountId: '',
    realBalance: '',
  }
}
