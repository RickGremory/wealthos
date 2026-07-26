import type { CommitmentNextActionType, CommitmentNextActionView } from '~/types/commitments'

export function getNextActionTitle(type: CommitmentNextActionType | string): string {
  switch (type) {
    case 'pay_overdue':
      return 'Pagar vencido'
    case 'pay_minimum':
      return 'Pagar mínimo'
    case 'pay_priority_debt':
      return 'Priorizar este pago'
    case 'configure_payment':
      return 'Configurar pago'
    case 'configure_interest_rate':
      return 'Registrar tasa'
    case 'review_paused':
      return 'Revisar pausa'
    case 'no_action_required':
      return 'Sin acción requerida'
    default:
      return 'Siguiente paso'
  }
}

export function getNextActionTone(
  type: CommitmentNextActionType | string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'teal' {
  if (type === 'pay_overdue') return 'danger'
  if (type === 'pay_minimum' || type === 'pay_priority_debt') return 'warning'
  if (type === 'configure_payment' || type === 'configure_interest_rate') return 'teal'
  if (type === 'no_action_required') return 'success'
  return 'neutral'
}

export function describeNextAction(action: CommitmentNextActionView | null): string {
  if (!action) return 'Sin recomendación todavía.'
  if (action.type === 'no_action_required') return 'Esta obligación no requiere acción ahora.'
  if (action.type === 'configure_payment') return 'Define un pago mínimo o programado.'
  if (action.type === 'configure_interest_rate') {
    return 'La estrategia Avalancha necesita la tasa anual.'
  }
  if (action.type === 'review_paused') return 'Revisa si conviene reactivar esta obligación.'
  return getNextActionTitle(action.type)
}
