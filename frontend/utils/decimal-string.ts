/**
 * Decimal string helpers for UI summaries.
 * Avoid floating point for ledger math; use integer cents under the hood.
 */

function toCents(value: string): bigint {
  const trimmed = value.trim() || '0'
  const sign = trimmed.startsWith('-') ? -1n : 1n
  const unsigned = trimmed.replace(/^[+-]/, '')
  const [integerPart = '0', fractionRaw = ''] = unsigned.split('.')
  const fraction = `${fractionRaw}00`.slice(0, 2)
  const cents = BigInt(integerPart || '0') * 100n + BigInt(fraction || '0')
  return sign * cents
}

function fromCents(cents: bigint): string {
  const sign = cents < 0n ? '-' : ''
  const abs = cents < 0n ? -cents : cents
  const whole = abs / 100n
  const frac = (abs % 100n).toString().padStart(2, '0')
  return `${sign}${whole}.${frac}`
}

export function addDecimalStrings(...values: string[]): string {
  let total = 0n
  for (const value of values) {
    total += toCents(value)
  }
  return fromCents(total)
}

export function negateDecimalString(value: string): string {
  const cents = toCents(value)
  return fromCents(-cents)
}

export function absDecimalString(value: string): string {
  const cents = toCents(value)
  return fromCents(cents < 0n ? -cents : cents)
}

export function compareDecimalStrings(a: string, b: string): number {
  const diff = toCents(a) - toCents(b)
  if (diff === 0n) return 0
  return diff < 0n ? -1 : 1
}

export function isZeroDecimalString(value: string): boolean {
  return toCents(value) === 0n
}
