import type { GoalDisplayStatus, GoalStatus } from '~/types/goals'
import { compareDecimalStrings } from '~/utils/decimal-string'

export interface GoalStatusInput {
  status: GoalStatus
  targetDate: string | null
  estimatedCompletionDate: string | null
  completionPercentage: string
  /** ISO date or Date used as "today" for tests. Defaults to now. */
  asOf?: string | Date
}

export interface GoalDisplayStatusMeta {
  status: GoalDisplayStatus
  label: string
  tone: 'teal' | 'success' | 'warning' | 'neutral'
  hint?: string
}

function toDateOnly(value: string | Date): Date {
  if (value instanceof Date) {
    return new Date(value.getFullYear(), value.getMonth(), value.getDate())
  }
  const [y, m, d] = value.slice(0, 10).split('-').map(Number)
  return new Date(y!, (m ?? 1) - 1, d ?? 1)
}

function daysBetween(from: Date, to: Date): number {
  const ms = to.getTime() - from.getTime()
  return Math.floor(ms / (24 * 60 * 60 * 1000))
}

function parsePercent(value: string): number {
  const n = Number.parseFloat(value)
  return Number.isFinite(n) ? n : 0
}

/**
 * Derive UI display status. Never uses red/danger — behind is amber with positive copy.
 */
export function deriveGoalDisplayStatus(input: GoalStatusInput): GoalDisplayStatusMeta {
  if (input.status === 'archived') {
    return {
      status: 'paused',
      label: 'En pausa',
      tone: 'neutral',
      hint: 'Archivada · el historial sigue disponible',
    }
  }

  if (input.status === 'completed') {
    return {
      status: 'completed',
      label: 'Completada',
      tone: 'success',
    }
  }

  const asOf = toDateOnly(input.asOf ?? new Date())
  const completion = parsePercent(input.completionPercentage)

  if (input.targetDate) {
    const target = toDateOnly(input.targetDate)

    if (input.estimatedCompletionDate) {
      const estimated = toDateOnly(input.estimatedCompletionDate)
      if (estimated.getTime() > target.getTime()) {
        return {
          status: 'behind',
          label: 'Ajusta el ritmo',
          tone: 'warning',
          hint: 'La proyección supera la fecha objetivo',
        }
      }
    }

    // Progress vs elapsed time (created unknown → use a soft window from target).
    // If target is in the past and not complete → behind.
    if (target.getTime() < asOf.getTime() && completion < 100) {
      return {
        status: 'behind',
        label: 'Ajusta el ritmo',
        tone: 'warning',
        hint: 'La fecha objetivo ya pasó',
      }
    }

    // If we have both dates and can estimate elapsed vs remaining window:
    // Compare completion % to expected % if linear from 90 days before target (fallback window).
    const windowStart = new Date(target)
    windowStart.setDate(windowStart.getDate() - 90)
    const totalDays = Math.max(1, daysBetween(windowStart, target))
    const elapsedDays = Math.max(0, Math.min(totalDays, daysBetween(windowStart, asOf)))
    const expectedPct = (elapsedDays / totalDays) * 100

    if (elapsedDays > 7 && completion + 15 < expectedPct) {
      return {
        status: 'behind',
        label: 'Ajusta el ritmo',
        tone: 'warning',
        hint: 'El avance va un poco detrás del tiempo',
      }
    }

    if (completion >= expectedPct - 5 || !input.targetDate) {
      return {
        status: 'on_track',
        label: 'En camino',
        tone: 'teal',
      }
    }
  }

  if (compareDecimalStrings(input.completionPercentage, '0') > 0) {
    return {
      status: 'on_track',
      label: 'En camino',
      tone: 'teal',
    }
  }

  return {
    status: 'active',
    label: 'Activa',
    tone: 'teal',
  }
}
