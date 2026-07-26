import type { CommitmentDisplayStatus, CommitmentStatus } from '~/types/commitments'

export interface CommitmentStatusMeta {
  label: string
  tone: 'neutral' | 'success' | 'warning' | 'danger' | 'teal'
  hint?: string
}

const DISPLAY: Record<CommitmentDisplayStatus, CommitmentStatusMeta> = {
  active: { label: 'Activa', tone: 'teal' },
  due_soon: { label: 'Por vencer', tone: 'warning', hint: 'Vence en los próximos 7 días' },
  overdue: { label: 'Vencida', tone: 'danger', hint: 'Pago atrasado' },
  settled: { label: 'Al corriente', tone: 'success', hint: 'Saldo en cero (revolving)' },
  paid_off: { label: 'Liquidada', tone: 'success' },
  paused: { label: 'Pausada', tone: 'neutral' },
  defaulted: { label: 'En mora', tone: 'danger' },
  archived: { label: 'Archivada', tone: 'neutral' },
}

export function getCommitmentDisplayMeta(
  displayStatus: CommitmentDisplayStatus | string | null | undefined,
  status?: CommitmentStatus,
): CommitmentStatusMeta {
  if (displayStatus && displayStatus in DISPLAY) {
    return DISPLAY[displayStatus as CommitmentDisplayStatus]
  }
  if (status === 'paused') return DISPLAY.paused
  if (status === 'archived') return DISPLAY.archived
  if (status === 'defaulted') return DISPLAY.defaulted
  if (status === 'closed') return DISPLAY.paid_off
  return DISPLAY.active
}

export function isAttentionStatus(displayStatus: string | null | undefined): boolean {
  return displayStatus === 'overdue'
    || displayStatus === 'due_soon'
    || displayStatus === 'defaulted'
}
