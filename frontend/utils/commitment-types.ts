import type { CommitmentType } from '~/types/commitments'

export interface CommitmentTypeOption {
  value: CommitmentType
  label: string
  accountHint: 'credit_card' | 'loan'
}

export const COMMITMENT_TYPE_OPTIONS: CommitmentTypeOption[] = [
  { value: 'credit_card', label: 'Tarjeta de crédito', accountHint: 'credit_card' },
  { value: 'line_of_credit', label: 'Línea de crédito', accountHint: 'credit_card' },
  { value: 'personal_loan', label: 'Préstamo personal', accountHint: 'loan' },
  { value: 'auto_loan', label: 'Crédito automotriz', accountHint: 'loan' },
  { value: 'mortgage', label: 'Hipoteca', accountHint: 'loan' },
  { value: 'student_loan', label: 'Crédito educativo', accountHint: 'loan' },
  { value: 'business_loan', label: 'Crédito empresarial', accountHint: 'loan' },
  { value: 'family_loan', label: 'Préstamo familiar', accountHint: 'loan' },
  { value: 'installment_plan', label: 'Plan a meses', accountHint: 'loan' },
  { value: 'other', label: 'Otro', accountHint: 'loan' },
]

export function getCommitmentTypeLabel(type: string): string {
  return COMMITMENT_TYPE_OPTIONS.find(o => o.value === type)?.label ?? type
}

export function getAccountHintForType(type: CommitmentType): 'credit_card' | 'loan' {
  return COMMITMENT_TYPE_OPTIONS.find(o => o.value === type)?.accountHint ?? 'loan'
}

export function getCommitmentPriorityLabel(priority: string): string {
  if (priority === 'high') return 'Alta'
  if (priority === 'low') return 'Baja'
  return 'Media'
}
