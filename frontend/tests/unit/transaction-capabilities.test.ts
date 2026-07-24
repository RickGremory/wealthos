import { describe, expect, it } from 'vitest'
import { getAccountCapabilities } from '../../utils/transaction-capabilities'

describe('transaction-capabilities', () => {
  it('allows income/expense/transfer on checking', () => {
    const caps = getAccountCapabilities('checking')
    expect(caps.canReceiveIncome).toBe(true)
    expect(caps.canPayExpense).toBe(true)
    expect(caps.canTransferFrom).toBe(true)
    expect(caps.canTransferTo).toBe(true)
    expect(caps.canAdjust).toBe(true)
  })

  it('restricts credit card: expense yes, income no, transfer no', () => {
    const caps = getAccountCapabilities('credit_card')
    expect(caps.canPayExpense).toBe(true)
    expect(caps.canReceiveIncome).toBe(false)
    expect(caps.canTransferFrom).toBe(false)
    expect(caps.canTransferTo).toBe(true)
  })

  it('restricts loan to transfer-in and adjust only', () => {
    const caps = getAccountCapabilities('loan')
    expect(caps.canReceiveIncome).toBe(false)
    expect(caps.canPayExpense).toBe(false)
    expect(caps.canTransferFrom).toBe(false)
    expect(caps.canTransferTo).toBe(true)
    expect(caps.canAdjust).toBe(true)
  })

  it('blocks expense on investment', () => {
    expect(getAccountCapabilities('investment').canPayExpense).toBe(false)
    expect(getAccountCapabilities('investment').canReceiveIncome).toBe(true)
  })
})
