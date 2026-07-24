import { describe, expect, it } from 'vitest'
import {
  toBackendAccountType,
  toOpeningBalancePayload,
  toSimplifiedAccountType,
} from '../../utils/account-type-mapper'

describe('account-type-mapper', () => {
  it('maps simplified types to backend types', () => {
    expect(toBackendAccountType('checking')).toBe('checking')
    expect(toBackendAccountType('credit_card')).toBe('credit_card')
    expect(toBackendAccountType('other')).toBe('other')
  })

  it('maps backend types back to simplified types', () => {
    expect(toSimplifiedAccountType('savings')).toBe('savings')
    expect(toSimplifiedAccountType('investment')).toBe('other')
    expect(toSimplifiedAccountType('unknown')).toBe('other')
  })

  it('keeps asset opening balances as positive decimal strings', () => {
    expect(toOpeningBalancePayload('checking', '1500.50')).toBe('1500.50')
    expect(toOpeningBalancePayload('cash', '100')).toBe('100.00')
  })

  it('sends negative opening_balance for credit card debt entered as positive', () => {
    expect(toOpeningBalancePayload('credit_card', '2500.00')).toBe('-2500.00')
    expect(toOpeningBalancePayload('credit_card', '800')).toBe('-800.00')
  })

  it('keeps zero credit card balances at 0.00', () => {
    expect(toOpeningBalancePayload('credit_card', '0')).toBe('0.00')
    expect(toOpeningBalancePayload('credit_card', '0.00')).toBe('0.00')
  })
})
