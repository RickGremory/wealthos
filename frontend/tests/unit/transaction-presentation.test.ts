import { describe, expect, it } from 'vitest'
import {
  displayAmountMagnitude,
  getPresentationSign,
  presentTransaction,
  presentTransactionType,
} from '../../utils/transaction-presentation'

describe('transaction-presentation', () => {
  it('labels types in Spanish', () => {
    expect(presentTransactionType('expense')).toBe('Gasto')
    expect(presentTransactionType('income')).toBe('Ingreso')
    expect(presentTransactionType('transfer')).toBe('Transferencia')
    expect(presentTransactionType('adjustment')).toBe('Ajuste')
  })

  it('assigns presentation signs', () => {
    expect(getPresentationSign('income')).toBe('positive')
    expect(getPresentationSign('expense')).toBe('negative')
    expect(getPresentationSign('transfer')).toBe('neutral')
    expect(getPresentationSign('adjustment', '25.00')).toBe('positive')
    expect(getPresentationSign('adjustment', '-10.00')).toBe('negative')
  })

  it('adds credit card expense hint', () => {
    const p = presentTransaction({
      type: 'expense',
      status: 'posted',
      accountType: 'credit_card',
    })
    expect(p.amountPrefix).toBe('-')
    expect(p.impactHint).toMatch(/tarjeta/i)
  })

  it('strips sign for magnitude display', () => {
    expect(displayAmountMagnitude('-12.50')).toBe('12.50')
    expect(displayAmountMagnitude('+3.00')).toBe('3.00')
    expect(displayAmountMagnitude(null)).toBe('0.00')
  })
})
