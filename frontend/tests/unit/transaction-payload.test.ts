import { describe, expect, it } from 'vitest'
import {
  buildCreateTransactionPayload,
  buildOccurredAtIso,
  computeAdjustmentDelta,
  emptyTransactionForm,
  toApiCreateBody,
  validateTransactionForm,
} from '../../utils/transaction-payload'

describe('transaction-payload', () => {
  it('builds expense body with positive amount and category default description', () => {
    const form = emptyTransactionForm('expense', new Date(2026, 6, 24))
    form.accountId = 'acc-1'
    form.categoryId = 'cat-1'
    form.amount = '150.5'
    form.description = ''
    form.occurredDate = '2026-07-20'

    const input = buildCreateTransactionPayload({
      form,
      categoryName: 'Comida',
      now: new Date(2026, 6, 24, 10, 0, 0),
    })
    expect(input).toMatchObject({
      transactionType: 'expense',
      accountId: 'acc-1',
      categoryId: 'cat-1',
      amount: '150.50',
      description: 'Comida',
    })

    const body = toApiCreateBody(input)
    expect(body).toMatchObject({
      transaction_type: 'expense',
      account_id: 'acc-1',
      category_id: 'cat-1',
      amount: '150.50',
      description: 'Comida',
    })
    expect(body.occurred_at).toBeTruthy()
  })

  it('builds transfer body without category', () => {
    const form = emptyTransactionForm('transfer')
    form.sourceAccountId = 'a'
    form.destinationAccountId = 'b'
    form.amount = '10.00'
    form.description = 'Traspaso'
    form.occurredDate = '2026-07-24'

    const body = toApiCreateBody(buildCreateTransactionPayload({ form }))
    expect(body.transaction_type).toBe('transfer')
    expect(body.source_account_id).toBe('a')
    expect(body.destination_account_id).toBe('b')
    expect(body.category_id).toBeUndefined()
  })

  it('computes signed adjustment delta from real balance', () => {
    expect(computeAdjustmentDelta('1200.00', '1000.00')).toBe('200.00')
    expect(computeAdjustmentDelta('900.00', '1000.00')).toBe('-100.00')

    const form = emptyTransactionForm('adjustment')
    form.accountId = 'acc-1'
    form.realBalance = '900.00'
    form.description = 'Corrección de saldo'
    form.occurredDate = '2026-07-24'

    const input = buildCreateTransactionPayload({
      form,
      currentBalance: '1000.00',
    })
    expect(input.transactionType).toBe('adjustment')
    if (input.transactionType === 'adjustment') {
      expect(input.amount).toBe('-100.00')
    }
  })

  it('validates required fields', () => {
    const form = emptyTransactionForm('expense')
    const errors = validateTransactionForm(form)
    expect(errors.some(e => e.field === 'amount')).toBe(true)
    expect(errors.some(e => e.field === 'accountId')).toBe(true)
    expect(errors.some(e => e.field === 'categoryId')).toBe(true)
  })

  it('uses noon local for past dates and now for today', () => {
    const now = new Date(2026, 6, 24, 18, 30, 0)
    const past = buildOccurredAtIso({ date: '2026-07-20', now })
    expect(new Date(past).getHours()).toBe(12)

    const today = buildOccurredAtIso({ date: '2026-07-24', now })
    expect(today).toBe(now.toISOString())
  })
})
