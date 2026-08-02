import { describe, expect, it } from 'vitest'
import {
  deriveEffectiveExchangeRate,
  formatFxRateLabel,
} from '~/utils/fx-transfer'

describe('deriveEffectiveExchangeRate', () => {
  it('derives MXN per USD from real conversion amounts', () => {
    expect(deriveEffectiveExchangeRate('1803.95', '100.00')).toBe('18.0395')
  })

  it('returns null when amounts are missing or zero', () => {
    expect(deriveEffectiveExchangeRate('', '100')).toBeNull()
    expect(deriveEffectiveExchangeRate('100', '0')).toBeNull()
  })
})

describe('formatFxRateLabel', () => {
  it('formats source-per-destination label', () => {
    expect(formatFxRateLabel('18.0395', 'MXN', 'USD')).toBe(
      '18.0395 MXN por USD',
    )
  })
})
