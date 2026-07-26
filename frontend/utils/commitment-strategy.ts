import type { PaymentStrategy } from '~/types/commitments'

export function getPaymentStrategyLabel(strategy: PaymentStrategy | string): string {
  switch (strategy) {
    case 'avalanche':
      return 'Avalancha'
    case 'snowball':
      return 'Bola de nieve'
    case 'minimum_only':
      return 'Solo mínimos'
    case 'manual':
      return 'Manual'
    default:
      return strategy
  }
}

export function getPaymentStrategyDescription(strategy: PaymentStrategy | string): string {
  switch (strategy) {
    case 'avalanche':
      return 'Prioriza la tasa de interés más alta para reducir el costo total.'
    case 'snowball':
      return 'Prioriza el saldo más bajo para cerrar obligaciones más rápido.'
    case 'minimum_only':
      return 'Ordena por fecha de pago; sin empujar más allá del mínimo.'
    case 'manual':
      return 'Tú defines el orden con la prioridad de cada obligación.'
    default:
      return ''
  }
}

export function getStrategyReasonLabel(code: string): string {
  const map: Record<string, string> = {
    overdue: 'Pago vencido',
    due_soon: 'Por vencer',
    highest_interest_rate: 'Mayor tasa de interés',
    lowest_balance: 'Menor saldo',
    manual_priority: 'Prioridad manual',
    minimum_payment_required: 'Pago mínimo requerido',
    missing_interest_rate: 'Falta tasa de interés',
    missing_payment_schedule: 'Falta pago programado',
    defaulted_commitment: 'En mora',
  }
  return map[code] ?? code
}

export const PAYMENT_STRATEGY_OPTIONS: { value: PaymentStrategy, label: string }[] = [
  { value: 'avalanche', label: 'Avalancha' },
  { value: 'snowball', label: 'Bola de nieve' },
  { value: 'minimum_only', label: 'Solo mínimos' },
  { value: 'manual', label: 'Manual' },
]
