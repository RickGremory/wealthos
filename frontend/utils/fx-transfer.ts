import { isZeroDecimalString } from '~/utils/decimal-string'
import { normalizeUnsignedAmount } from '~/utils/transaction-payload'

/** Effective rate: units of source currency per 1 unit of destination. */
export function deriveEffectiveExchangeRate(
  sourceAmount: string,
  destinationAmount: string,
): string | null {
  const src = normalizeUnsignedAmount(sourceAmount)
  const dst = normalizeUnsignedAmount(destinationAmount)
  if (!src || !dst || isZeroDecimalString(src) || isZeroDecimalString(dst)) {
    return null
  }
  const srcNum = Number(src)
  const dstNum = Number(dst)
  if (!Number.isFinite(srcNum) || !Number.isFinite(dstNum) || dstNum === 0) {
    return null
  }
  // Display up to 6 significant decimals without trailing noise
  const rate = srcNum / dstNum
  const fixed = rate.toFixed(6).replace(/\.?0+$/, '')
  return fixed.includes('.') ? fixed : `${fixed}.0`
}

export function formatFxRateLabel(
  rate: string | null,
  sourceCurrency: string,
  destinationCurrency: string,
): string | null {
  if (!rate) return null
  return `${rate} ${sourceCurrency} por ${destinationCurrency}`
}
