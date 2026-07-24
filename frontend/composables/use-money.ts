/**
 * Display-only money helpers.
 * NEVER use Number() / parseFloat() for financial math — only for Intl formatting.
 */

export function parseDecimalString(value: string | null | undefined): {
  sign: 1 | -1
  integer: string
  fraction: string
  raw: string
} | null {
  if (value == null) return null
  const trimmed = String(value).trim()
  if (!trimmed || trimmed === '-' || trimmed === '+' || trimmed === '.') return null

  const sign: 1 | -1 = trimmed.startsWith('-') ? -1 : 1
  const unsigned = trimmed.replace(/^[+-]/, '')
  const [integerPart = '0', fractionPart = ''] = unsigned.split('.')
  const integer = integerPart.replace(/^0+(?=\d)/, '') || '0'
  const fraction = fractionPart.replace(/0+$/, '')

  return { sign, integer, fraction, raw: trimmed }
}

export function isNegativeDecimal(value: string | null | undefined): boolean {
  const parsed = parseDecimalString(value)
  if (!parsed) return false
  if (parsed.sign === 1) return false
  return !(parsed.integer === '0' && !parsed.fraction)
}

export function formatMoney(
  amount: string | null | undefined,
  currency: string,
  locale = 'es-MX',
): string {
  if (amount == null || amount === '') return '—'

  // Intl needs a number for display only; we avoid arithmetic.
  const numeric = Number(amount)
  if (!Number.isFinite(numeric)) return String(amount)

  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numeric)
  } catch {
    return `${amount} ${currency}`
  }
}

export function useMoney() {
  const preferences = usePreferencesStore()

  function format(
    amount: string | null | undefined,
    currency: string,
    locale?: string,
  ) {
    if (preferences.hideBalances) return '••••'
    return formatMoney(amount, currency, locale ?? preferences.locale)
  }

  return {
    format,
    formatMoney,
    parseDecimalString,
    isNegativeDecimal,
  }
}
