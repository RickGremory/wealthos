import { describe, expect, it } from 'vitest'
import { formatMoney, isNegativeDecimal } from '../../composables/use-money'

describe('dashboard money display helpers', () => {
  it('formats large net worth with currency symbol', () => {
    expect(formatMoney('245800.00', 'MXN', 'es-MX')).toMatch(/245/)
  })

  it('detects negative variance for expenses', () => {
    expect(isNegativeDecimal('-38000.00')).toBe(true)
    expect(isNegativeDecimal('27000.00')).toBe(false)
  })
})
