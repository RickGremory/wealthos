import { describe, expect, it } from 'vitest'
import {
  absDecimalString,
  addDecimalStrings,
  compareDecimalStrings,
  isZeroDecimalString,
  negateDecimalString,
} from '../../utils/decimal-string'

describe('decimal-string', () => {
  it('adds decimal strings without floating point drift', () => {
    expect(addDecimalStrings('0.1', '0.2')).toBe('0.30')
    expect(addDecimalStrings('1000.50', '250.25')).toBe('1250.75')
    expect(addDecimalStrings('-8500.00', '1000.00')).toBe('-7500.00')
  })

  it('supports empty summands via zero default pattern', () => {
    expect(addDecimalStrings('0.00')).toBe('0.00')
    expect(addDecimalStrings()).toBe('0.00')
  })

  it('negates and absolutes', () => {
    expect(negateDecimalString('12.50')).toBe('-12.50')
    expect(negateDecimalString('-12.50')).toBe('12.50')
    expect(absDecimalString('-8500.00')).toBe('8500.00')
    expect(absDecimalString('8500.00')).toBe('8500.00')
  })

  it('compares and detects zero', () => {
    expect(compareDecimalStrings('1.00', '2.00')).toBeLessThan(0)
    expect(compareDecimalStrings('2.00', '1.00')).toBeGreaterThan(0)
    expect(compareDecimalStrings('1.00', '1.00')).toBe(0)
    expect(isZeroDecimalString('0')).toBe(true)
    expect(isZeroDecimalString('0.00')).toBe(true)
    expect(isZeroDecimalString('-0.00')).toBe(true)
    expect(isZeroDecimalString('0.01')).toBe(false)
  })
})
