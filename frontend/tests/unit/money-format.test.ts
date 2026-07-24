import { describe, expect, it } from 'vitest'
import {
  formatMoney,
  isNegativeDecimal,
  parseDecimalString,
} from '../../composables/use-money'

describe('formatMoney', () => {
  it('formats a decimal string with currency', () => {
    const result = formatMoney('1234.50', 'MXN', 'es-MX')
    expect(result).toContain('1')
    expect(result).toMatch(/234/)
  })

  it('returns em dash for null/empty', () => {
    expect(formatMoney(null, 'MXN')).toBe('—')
    expect(formatMoney('', 'USD')).toBe('—')
  })

  it('falls back for non-numeric strings', () => {
    expect(formatMoney('n/a', 'MXN')).toBe('n/a')
  })
})

describe('parseDecimalString', () => {
  it('parses sign and parts without Number math', () => {
    expect(parseDecimalString('-42.10')).toEqual({
      sign: -1,
      integer: '42',
      fraction: '1',
      raw: '-42.10',
    })
  })

  it('returns null for blank', () => {
    expect(parseDecimalString('')).toBeNull()
    expect(parseDecimalString(null)).toBeNull()
  })
})

describe('isNegativeDecimal', () => {
  it('detects negative amounts', () => {
    expect(isNegativeDecimal('-0.01')).toBe(true)
    expect(isNegativeDecimal('10')).toBe(false)
    expect(isNegativeDecimal('-0.00')).toBe(false)
  })
})
